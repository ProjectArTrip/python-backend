from arttrip.application.util.exception import DomainException, ErrorCode


class UserError(DomainException):
    @classmethod
    def blank_nickname(cls) -> "UserError":
        return cls(code="USER_NICKNAME_BLANK", message="닉네임을 입력해 주세요.")

    @classmethod
    def provider_already_linked(cls) -> "UserError":
        return cls(
            code="USER_PROVIDER_ALREADY_LINKED",
            message="이미 연결된 소셜 계정입니다.",
            error_code=ErrorCode.ALREADY_EXISTS,
        )

    @classmethod
    def role_already_selected(cls) -> "UserError":
        return cls(
            code="USER_ROLE_ALREADY_SELECTED",
            message="이미 선택된 권한입니다.",
        )

    @classmethod
    def role_not_selectable(cls) -> "UserError":
        return cls(
            code="USER_ROLE_NOT_SELECTABLE", message="선택할 수 없는 권한입니다."
        )

    @classmethod
    def invalid_nickname(cls) -> "UserError":
        return cls(
            code="USER_NICKNAME_INVALID",
            message="닉네임은 2~10자의 한글, 영문, 숫자로 입력해 주세요.",
        )

    @classmethod
    def duplicated_nickname(cls) -> "UserError":
        return cls(
            code="USER_NICKNAME_DUPLICATED",
            message="중복된 닉네임입니다.",
            error_code=ErrorCode.ALREADY_EXISTS,
        )

    @classmethod
    def keyword_step_not_reached(cls) -> "UserError":
        return cls(
            code="USER_KEYWORD_STEP_NOT_REACHED",
            message="이전 온보딩 단계를 먼저 완료해 주세요.",
        )

    @classmethod
    def genre_keyword_required(cls) -> "UserError":
        return cls(
            code="USER_GENRE_KEYWORD_REQUIRED",
            message="장르 키워드를 한 가지 이상 선택해 주세요.",
        )

    @classmethod
    def artist_verification_not_allowed(cls) -> "UserError":
        return cls(
            code="USER_ARTIST_VERIFICATION_NOT_ALLOWED",
            message="일반 사용자만 아티스트 인증을 신청할 수 있습니다.",
            error_code=ErrorCode.ALREADY_EXISTS,
        )

    @classmethod
    def admin_cannot_delete_account(cls) -> "UserError":
        return cls(
            code="USER_ADMIN_ACCOUNT_DELETION_NOT_ALLOWED",
            message="관리자 계정은 탈퇴할 수 없습니다.",
            error_code=ErrorCode.PERMISSION_DENIED,
        )

    @classmethod
    def artist_role_required(cls) -> "UserError":
        return cls(
            code="USER_ARTIST_ROLE_REQUIRED",
            message="인증된 아티스트만 이용할 수 있습니다.",
            error_code=ErrorCode.PERMISSION_DENIED,
        )

    @classmethod
    def role_step_not_reached(cls) -> "UserError":
        return cls(
            code="USER_ROLE_STEP_NOT_REACHED",
            message="닉네임을 먼저 설정해 주세요.",
        )

    @classmethod
    def nickname_step_already_completed(cls) -> "UserError":
        return cls(
            code="USER_NICKNAME_STEP_ALREADY_COMPLETED",
            message="이미 닉네임 설정을 마쳤습니다.",
        )

    @classmethod
    def keyword_step_already_completed(cls) -> "UserError":
        return cls(
            code="USER_KEYWORD_STEP_ALREADY_COMPLETED",
            message="이미 관심 키워드 설정을 마쳤습니다.",
        )
