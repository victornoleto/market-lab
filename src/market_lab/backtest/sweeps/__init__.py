"""ai_trade.backtest.sweeps — fan-out sweep registry helpers.

See specs/self_improve_fanout_mode.md and
docs/self_improvement/fanout_protocol.md for the full protocol. This
package provides the Python helpers the self-improve loop agent uses
when SWEEP_MODE=fanout:

- ``registry.load_registry(path)``
- ``registry.validate_schema_v1(registry_dict)``
- ``registry.atomic_write_registry(path, registry_dict)``
- ``registry.append_done(registry_dict, summary)``
- ``registry.pop_pending(registry_dict)``
- ``registry.mark_errored(registry_dict, ticker, error_msg, iter_num)``

Schema versioning is strict equality (v1 only at the moment). Any
change to the schema requires bumping ``SCHEMA_VERSION`` and writing
a migration helper alongside it.
"""

from ai_trade.backtest.sweeps.registry import (
    SCHEMA_VERSION,
    RegistryValidationError,
    append_done,
    atomic_write_registry,
    load_registry,
    mark_errored,
    pop_pending,
    validate_schema_v1,
)

__all__ = [
    "SCHEMA_VERSION",
    "RegistryValidationError",
    "append_done",
    "atomic_write_registry",
    "load_registry",
    "mark_errored",
    "pop_pending",
    "validate_schema_v1",
]
