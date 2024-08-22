# CST Studio Pipeline

CST Studio Pipeline is a Python program designed to extract and process data from various sources efficiently. It provides a flexible and customizable pipeline for data extraction tasks.

## Installation

Clone the repository using Git:

```bash
git clone https://github.com/brushwayne/cst_studio-pipeline.git
```

Create a virtual environment

```bash
python -m venv VENV
```

Activate the virtual environment depending on your Operating System then install the required dependencies:

```bash
pip --no-cahce-dir install -r requirements.txt
```

## Running 

```bash
cd cst_studio-pipeline
python main.py
```

## Building for windows

```bash
python setup.py build
```
Then you can go into the `build` directory and run the executable file to do the work in your computer dr saaar. PLz ssaaar give me atttendence saaar....


## Usage

Follow the instructions and configure the pipeline according to your data extraction requirements.

![alt text](assets/image.png)

1. Check the parameters which you want to extract.
2. Click on `S11 File` to select the output of your exported ASCII S11 file.
3. Click on `Gain File` to select the output of your exported ASCII Gain file.
4. Click on `Result File` to specify the output file _(ideally a `.csv` empty file)_.
5. Click calculate to start the process and wait to finish.

## Contributing

Contributions are welcome! If you'd like to contribute to CST Studio Pipeline, please fork the repository and submit a pull request with your changes. For licensing, read [LICENSE](LICENSE).
