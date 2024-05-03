__doc__ = """Timestepping utilities to be used with Rod and RigidBody classes"""

from typing import Tuple, List, Callable, Type, Any, overload
from elastica.typing import SystemType, SystemCollectionType, SteppersOperatorsType

import numpy as np
from tqdm import tqdm

from elastica.systems import is_system_a_collection

from .symplectic_steppers import PositionVerlet, PEFRL
from .explicit_steppers import RungeKutta4, EulerForward

from .protocol import StepperProtocol, SymplecticStepperProtocol


# Deprecated: Remove in the future version
# Many script still uses this method to control timestep. Keep it for backward compatibility
def extend_stepper_interface(
    stepper: StepperProtocol, system_collection: SystemCollectionType
) -> Tuple[
    Callable[
        [StepperProtocol, SystemCollectionType, np.floating, np.floating], np.floating
    ],
    SteppersOperatorsType,
]:
    # Check if system is a "collection" of smaller systems
    assert is_system_a_collection(
        system_collection
    ), "Only system-collection type can be used for timestepping. Use BaseSystemCollection."

    try:
        stepper_methods: SteppersOperatorsType = stepper.steps_and_prefactors
        do_step_method: Callable = stepper.do_step  # type: ignore[attr-defined]
    except AttributeError as e:
        raise NotImplementedError(f"{stepper} stepper is not supported.") from e
    return do_step_method, stepper_methods


def integrate(
    stepper: StepperProtocol,
    systems: SystemType | SystemCollectionType,
    final_time: float,
    n_steps: int = 1000,
    restart_time: float = 0.0,
    progress_bar: bool = True,
) -> float:
    """

    Parameters
    ----------
    stepper : StepperProtocol
        Stepper algorithm to use.
    systems : SystemType | SystemCollectionType
        The elastica-system to simulate.
    final_time : float
        Total simulation time. The timestep is determined by final_time / n_steps.
    n_steps : int
        Number of steps for the simulation. (default: 1000)
    restart_time : float
        The timestamp of the first integration step. (default: 0.0)
    progress_bar : bool
        Toggle the tqdm progress bar. (default: True)
    """
    assert final_time > 0.0, "Final time is negative!"
    assert n_steps > 0, "Number of integration steps is negative!"

    dt = np.float_(float(final_time) / n_steps)
    time = np.float_(restart_time)

    if is_system_a_collection(systems):
        for i in tqdm(range(n_steps), disable=(not progress_bar)):
            time = stepper.step(systems, time, dt)  # type: ignore[arg-type]
    else:
        for i in tqdm(range(n_steps), disable=(not progress_bar)):
            time = stepper.step_single_instance(systems, time, dt)  # type: ignore[arg-type]

    print("Final time of simulation is : ", time)
    return float(time)
