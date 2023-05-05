import argparse
import sys
import time
from functools import partial
from typing import Tuple

import cv2
import numpy as np
from tqdm import trange

from toolbox.Models import model_catalog


def count_time(c: callable) -> Tuple[float, any]:
    ti = time.time()
    ret = c()
    tf = time.time()
    return tf-ti, ret


def benchmark_model(model_name: str, method: str, n: int, call_input: any,
                    model_params: dict) -> dict:
    print("model_name:", model_name)
    print("method:", method)
    print("n:", n)
    print("call_input:", f"np.ndarray {call_input.shape}" if
          isinstance(call_input, np.ndarray) else call_input)
    print("model_params:", model_params)

    times = {"load": 0., "min": 0, "mean": 0, "max": 0, "total": 0, "op/s": 0}

    if model_name == "face_recognition_facenet":
        model = model_catalog[model_name](**model_params)
        times["load"], _ = count_time(lambda: model.load_model())
    else:
        times["load"], model = count_time(
            lambda: model_catalog[model_name](**model_params))

    call = getattr(model, method)
    assert call is not None, (dir(model), method)
    call = partial(call, call_input)
    run_times = []
    for _ in trange(n):
        t, _ = count_time(call)
        run_times.append(t)
    run_times = np.array(run_times)
    times["total"] = run_times.sum()
    times["mean"] = run_times.mean()
    times["min"] = run_times.min()
    times["max"] = run_times.max()
    times["op/s"] = n/run_times.sum()
    return times


def parse_args():
    ap = argparse.ArgumentParser(
        description="Benchmark a toolbox Model. "
        "e.g. > python benchmark_model.py -m age_gender -t 1000 "
        "age_model_path= gender_model_path= use_cuda=False"
    )
    ap.add_argument(
        "-m",
        "--model",
        help="Name of the model to benchmark"
    )
    ap.add_argument(
        "-n",
        "--n",
        default=100,
        type=int,
        help="Number of times to run the model. Defaults to 100"
    )
    ap.add_argument(
        "--method",
        default="predict",
        help="Model method to call. Defaults to 'predict'"
    )
    ap.add_argument(
        "--image",
        default=None,
        help="Optional input image"
    )
    ap.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List the name of the registered models"
    )
    ap.add_argument(
        "args",
        nargs="*",
        help="List of model parameters in the form of "
        "'param1=value param2_value ...'"
    )
    return ap.parse_args()


def parse_value(value: str) -> any:
    if value in ("None", "none", "null"):
        return None
    if value in ("False", "false"):
        return False
    if value in ("True", "true"):
        return True
    if "," in value:
        value = value.replace("[", "")
        value = value.replace("]", "")
        value = value.replace("(", "")
        value = value.replace(")", "")
        return [parse_value(v.strip()) for v in value.split(",")]
    try:
        value = float(value)
        if value.is_integer():
            return int(value)
        return value
    except:
        return value


if __name__ == "__main__":
    print(" ".join(sys.argv))
    args = parse_args()

    if args.list:
        print("\n".join(model_catalog.keys()))
        sys.exit(0)
    
    assert args.model is not None, "Model name is required"

    model_params = {
        a.split("=", maxsplit=1)[0]: parse_value(a.split("=", maxsplit=1)[1])
        for a in args.args
    }
    call_input = None
    if args.image is not None:
        call_input = cv2.imread(args.image)

    # Print the times formatted as a table and indicating the units
    times = benchmark_model(
        args.model, args.method, args.n, call_input, model_params
    )
    for k, v in times.items():
        print(f"{k}:\t{v} s")
