# Only for local.

check-ci:
	@act --rm push

check-ci-persist:
	@act push

check-ci-verbose:
	@act --rm -v push

check-ci-persist-verbose:
	@act -v push
