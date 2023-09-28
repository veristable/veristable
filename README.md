**VeriStable**: Harnessing Neuron Stability to Improve DNN Verification
====================

Content
====================
- ```src/```: source code

- ```benchmark/```: benchmarks for experiment

- ```results/```: experimental results

- ```env.yaml```: required packages


Installation
====================

## Dependencies
- [Anaconda](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- [Gurobi](https://www.gurobi.com/): Gurobi requires a license (a [free academic license](https://www.gurobi.com/downloads/free-academic-license/) is available).

## Installation
- Make sure you have `Anaconda`/`Miniconda` and `Gurobi` properly installed.

- Remove pre-installed environment 

```bash
conda deactivate 
conda env remove --name veristable
```

- Install required packages 

```bash
conda env create -f env.yaml
```


Getting Started
====================

## Usages

- Activate `conda` environment

```bash
conda activate veristable
```

- Minimal command

```python
python3 main.py --net ONNX_PATH --spec VNNLIB_PATH
```

- More options

```python
python3 main.py --net ONNX_PATH --spec VNNLIB_PATH 
               [--beam_candidate BEAM_CANDIDATE] [--stabilize_candidate STABILIZE_CANDIDATE]
               [--timeout TIMEOUT] [--device {cpu,cuda}]
               [--result_file RESULT_FILE] [--export_cex]
               [--disable_restart] [--disable_stabilize]
               [--verbosity {0,1,2}] [--test]
```

## Options
Use ```-h``` or ```--help``` to see options that can be passed into **VeriStable**. 

- `--net`: load pretrained ONNX model from this specified path.
- `--spec`: path to VNNLIB specification file.
- `--beam_candidate`: DPLL(T) search parallelism factor (`n`)
- `--stabilize_candidate`: stabilization parallelism factor (`k`)
- `--timeout`: timeout in seconds
- `--device`: device to use (either `cpu` or `cuda`).
- `--verbosity`: logging options (0: NOTSET, 1: INFO, 2: DEBUG).
- `--result_file`: file to save execution results.
- `--export_cex`: enable writing counter-example to `result_file`.
- `--disable_restart`: disable RESTART heuristic.
- `--disable_stabilize`: disable STABILIZE.
- `--test`: test on small example with special settings.



## Examples

- Unit test

```python
python3 test.py
```

- Examples showing **VeriStable** verifies properties (i.e., UNSAT results):

```python
python3 main.py --net "example/mnistfc-medium-net-554.onnx" --spec "example/test.vnnlib"
# unsat,29.7011
```

```python
python3 main.py --net "example/cifar10_2_255_simplified.onnx" --spec "example/cifar10_spec_idx_4_eps_0.00784_n1.vnnlib"
# unsat,20.0496
```

```python
python3 main.py --net "example/ACASXU_run2a_1_1_batch_2000.onnx" --spec "example/prop_6.vnnlib"
# unsat,4.3972
```

- Examples showing **VeriStable** disproves properties (i.e., SAT results):

```python
python3 main.py --net "example/ACASXU_run2a_1_9_batch_2000.onnx" --spec "example/prop_7.vnnlib"
# sat,4.2924
```

```python
python3 main.py --net "example/mnist-net_256x2.onnx" --spec "example/prop_1_0.05.vnnlib"
# sat,1.4306
```
