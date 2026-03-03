import logging
import structlog

def setup_logging(log_level: str = "INFO") -> None:
    """ Configure Stuctlog for structured JSON logging. """

    shared_processors = [
        structlog.contextvars.merge_contextvars,  # Merge context variables into log entries
        structlog.processors.add_log_level,       # Add log level to log entries
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),  # Add ISO 8601 timestamp
        structlog.processors.StackInfoRenderer(),  # Add stack info if available
    ]

    structlog.configure(
        processors= shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,  # Wrap for stdlib compatibility
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=[
            structlog.processors.JSONRenderer(),  # Render logs as JSON,
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,  # Remove processor metadata    
        ],
        foreign_pre_chain=shared_processors,  # Apply shared processors to stdlib logs
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
