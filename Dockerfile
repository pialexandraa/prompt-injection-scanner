FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Storing downloaded models in a location accessible to non-root users
ENV HF_HOME=/app/cache

WORKDIR /app

# Creating the user and cache directory first
RUN useradd -m sandboxuser \
    && mkdir -p /app/cache \
    && chown -R sandboxuser:sandboxuser /app

# Installing dependencies and pre-download the model weights as sandboxuser
USER sandboxuser
RUN pip install --no-cache-dir --user llm-guard \
    && python -c "from llm_guard.input_scanners import PromptInjection; PromptInjection()"

# Adding user's local bin to the PATH for any installed CLI tools
ENV PATH="/home/sandboxuser/.local/bin:$PATH"

COPY --chown=sandboxuser:sandboxuser scanner.py .

ENTRYPOINT ["python", "scanner.py"]