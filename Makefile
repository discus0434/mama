.PHONY: format lint lint-fix test post-change plan-review clean

format:
	uv run ruff format .

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check . --fix

test:
	uv run pytest

post-change:
	${MAKE} format
	${MAKE} lint
	${MAKE} test

plan-review:
	@test -n "$(PROMPT)" || (echo "PROMPT is required" >&2; exit 1)
	@OUTPUT=$${OUTPUT:-/tmp/plan-review.txt}; \
	IDLE_MS=$${IDLE_MS:-900000}; \
	codex exec -s read-only -c model_reasoning_effort="medium" -C . \
		-c "model_providers.openai.stream_idle_timeout_ms=$$IDLE_MS" \
		--output-last-message "$$OUTPUT" \
		"$$PROMPT"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
