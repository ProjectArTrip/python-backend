from datetime import UTC, date, datetime

import pytest
from arttrip.application.domain.review.review import (
    CONTENT_MAX_LENGTH,
    CONTENT_MIN_LENGTH,
    MAX_IMAGES,
    Review,
)
from arttrip.application.domain.review.review_image import ReviewImage
from arttrip.application.domain.review.review_status import ReviewStatus
from arttrip.application.util.exception import DomainException

NOW = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
TODAY = date(2026, 11, 23)
WRITER_ID = 1
OTHER_USER_ID = 2
ADMIN_ID = 99
VALID_CONTENT = "가볍게 보기 좋은 전시였어요. 추천합니다!"
BANNED = ("나쁜말",)


def written(*, image_keys: tuple[str, ...] = ()) -> Review:
    return Review.write(
        user_id=WRITER_ID,
        exhibit_id=10,
        content=VALID_CONTENT,
        visit_date=TODAY,
        image_keys=image_keys,
        banned_words=BANNED,
        today=TODAY,
        now=NOW,
    )


def with_stored_images(count: int) -> Review:
    review = written()
    review.images = [
        ReviewImage(
            id_=100 + order, image_key=f"reviews/{order}.jpg", display_order=order
        )
        for order in range(1, count + 1)
    ]
    return review


def revise(review: Review, **overrides: object) -> list[str]:
    arguments: dict[str, object] = {
        "editor_id": WRITER_ID,
        "content": VALID_CONTENT,
        "visit_date": TODAY,
        "delete_image_ids": (),
        "new_image_keys": (),
        "banned_words": BANNED,
        "today": TODAY,
        "now": NOW,
    }
    arguments.update(overrides)
    return review.revise(**arguments)  # type: ignore[arg-type]


class TestReview:
    def test_심사가_끝난_리뷰는_다시_심사할_수_없다(self) -> None:
        # given
        review = written()
        review.approve(reviewer_id=ADMIN_ID, now=NOW)

        # when
        with pytest.raises(DomainException) as raised:
            review.reject(reviewer_id=ADMIN_ID, reason="번복", now=NOW)

        # then
        assert raised.value.code == "REVIEW_NOT_PENDING"
        assert review.status is ReviewStatus.APPROVED

    def test_다른_사용자는_리뷰를_고칠_수_없고_있는지도_모른다(self) -> None:
        # given
        review = written()

        # when
        with pytest.raises(DomainException) as raised:
            revise(
                review,
                editor_id=OTHER_USER_ID,
                content="남이 바꾼 내용입니다 남이 바꾼 내용입니다",
            )

        # then
        assert raised.value.code == "REVIEW_NOT_FOUND"
        assert review.content == VALID_CONTENT

    def test_이_리뷰에_없는_사진_id_로는_지울_수_없다(self) -> None:
        # given
        review = with_stored_images(MAX_IMAGES)

        # when
        with pytest.raises(DomainException) as raised:
            revise(review, delete_image_ids=(999,), new_image_keys=("reviews/new.jpg",))

        # then
        assert raised.value.code == "REVIEW_IMAGE_NOT_FOUND"
        assert len(review.images) == MAX_IMAGES

    def test_사진이_상한을_한_장이라도_넘으면_막는다(self) -> None:
        # given
        too_many = tuple(f"reviews/{n}.jpg" for n in range(MAX_IMAGES + 1))

        # when
        with pytest.raises(DomainException) as raised:
            written(image_keys=too_many)

        # then
        assert raised.value.code == "REVIEW_TOO_MANY_IMAGES"

    def test_수정에서_사진_합계가_상한을_넘으면_아무것도_바꾸지_않는다(self) -> None:
        # given
        review = with_stored_images(MAX_IMAGES)
        new_content = "바뀐 내용입니다. 바뀐 내용입니다. 바뀐 내용"

        # when
        with pytest.raises(DomainException):
            revise(review, content=new_content, new_image_keys=("reviews/new.jpg",))

        # then
        assert review.content == VALID_CONTENT
        assert len(review.images) == MAX_IMAGES

    @pytest.mark.parametrize("length", [CONTENT_MIN_LENGTH - 1, CONTENT_MAX_LENGTH + 1])
    def test_본문_길이가_경계_밖이면_막는다(self, length: int) -> None:
        # when
        with pytest.raises(DomainException) as raised:
            Review.write(
                user_id=WRITER_ID,
                exhibit_id=10,
                content="가" * length,
                visit_date=TODAY,
                image_keys=(),
                banned_words=BANNED,
                today=TODAY,
                now=NOW,
            )

        # then
        assert raised.value.code == "REVIEW_CONTENT_INVALID"

    @pytest.mark.parametrize("disguised", ["나 쁜 말", "나1쁜2말", "나.쁜!말"])
    def test_끼워_넣은_글자로_금칙어를_피할_수_없다(self, disguised: str) -> None:
        # when
        with pytest.raises(DomainException) as raised:
            revise(
                written(),
                content=f"전시는 좋았지만 {disguised} 이 생각났어요. 다음에 또",
            )

        # then
        assert raised.value.code == "REVIEW_BANNED_WORD_INCLUDED"

    def test_미래_날짜는_방문일이_될_수_없다(self) -> None:
        # when
        with pytest.raises(DomainException) as raised:
            revise(written(), visit_date=date(2026, 11, 24))

        # then
        assert raised.value.code == "REVIEW_VISIT_DATE_IN_FUTURE"
