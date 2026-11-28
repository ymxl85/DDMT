"""ResNet V2 50: DD the recorded failures for flip and rotations +5/-5.

By default, reads the latest completed full ResNet failure search, including
existing find_mr_failures.py results. Use --failures RUN_DIR to choose a run,
--max-pairs N for a small trial, or --resume DD_RUN_DIR after interruption.
"""

from mr_pipeline_black import dd_main


if __name__ == "__main__":
    raise SystemExit(dd_main("resnet"))
