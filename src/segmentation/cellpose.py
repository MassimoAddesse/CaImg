import numpy as np
from cellpose import models

def segment_cells(
        stack: np.ndarray,
        diameter: float = 30,
        use_gpu: bool = True
) -> np.ndarray:

    std_projection = np.std(stack, axis = 0)

    model = models.CellposeModel(gpu = use_gpu)

    masks, _, _ = model.eval(
        std_projection,
        channels = [0,0],
        diameter = diameter,
        rescale = None
    )

    return masks
