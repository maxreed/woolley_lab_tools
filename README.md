# Woolley Lab Tools

A collection of Python (and PyMOL) scripts written by Max Reed for common tasks in the Woolley Lab. These tools cover UV-Vis spectral processing, size-exclusion chromatography data, mass spectrometry fragment identification, protein sequence formatting, NMR chemical-shift-based PDB colouring, and kinetic trace fitting.

This guide is written for people who may not have much programming experience. If you have never run a Python script before, don't worry -- follow the installation steps below and you will be up and running in a few minutes.

---

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Print Protein Sequence With Numbering](#print-protein-sequence-with-numbering)
3. [Process Spectra -- UV-Vis Spectrometer](#process-spectra----uv-vis-spectrometer)
4. [Process Spectra -- Plate Reader (Single Cuvette Measurements)](#process-spectra----plate-reader-single-cuvette-measurements)
5. [Other Spectra Scripts (Work in Progress)](#other-spectra-scripts-work-in-progress)
6. [Size Exclusion Chromatography Processing](#size-exclusion-chromatography-processing)
7. [Colour PDB by NMR Chemical Shift Perturbation](#colour-pdb-by-nmr-chemical-shift-perturbation)
8. [Mass Spec Degraded Protein Identifier](#mass-spec-degraded-protein-identifier)
9. [Process Multiple Thermal Reversion Traces for Tau](#process-multiple-thermal-reversion-traces-for-tau)
10. [Fill In CARA STR File (Advanced / Niche)](#fill-in-cara-str-file-advanced--niche)

---

## Installation and Setup

Most of these scripts need Python and a few scientific Python packages. The easiest way to get everything set up is with **Miniconda** (a lightweight version of Anaconda).

### Step 1: Install Miniconda

If you do not already have Conda installed:

1. Go to [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html).
2. Download the installer for your operating system (Mac, Windows, or Linux).
3. Run the installer. Accept the defaults -- they are fine for most people.
4. When it finishes, open a **new** terminal window (Mac/Linux: Terminal; Windows: Anaconda Prompt).
5. Type `conda --version` and press Enter. If you see a version number, you are good to go.

### Step 2: Create the environment

An **environment** is a self-contained set of Python packages that will not interfere with anything else on your computer. This repository includes an `environment.yml` file that lists everything you need.

In your terminal, navigate to the folder where you downloaded this repository, then run:

```bash
conda env create -f environment.yml
```

This will create an environment called `woolley_lab`.

### Step 3: Activate the environment

Every time you open a new terminal and want to use these scripts, activate the environment first:

```bash
conda activate woolley_lab
```

Your terminal prompt should now show `(woolley_lab)` at the beginning. You can now run any of the scripts described below.

### A note on PyMOL

One script in this collection (`colour_pdb/recolour_protein_GA17_updated.py`) is designed to run **inside PyMOL**, not from the regular terminal. See the [Colour PDB](#colour-pdb-by-nmr-chemical-shift-perturbation) section for details. You do not need the conda environment for that script -- it uses PyMOL's built-in Python interpreter.

---

## Print Protein Sequence With Numbering

**Script:** `printProteinSequenceWithNumbering.py`

### What it does

Takes a protein amino acid sequence and prints it in a nicely formatted, numbered layout -- 60 residues per line, grouped in blocks of 10, with position markers above. The output is meant to be pasted into a document using a monospaced font (e.g., Courier New) for figures, supplemental materials, or lab notebooks.

### How to use it

1. Open `printProteinSequenceWithNumbering.py` in any text editor.
2. Find the line near the top that looks like:
   ```python
   sequence = 'MRGSHHHHHHGS...'
   ```
   Replace the sequence between the quotes with your own protein sequence (single-letter amino acid codes, no spaces or line breaks).
3. (Optional) Adjust `lineLength` if you want more or fewer residues per line. The default of `66` gives 60 amino acids per line (you need 11 characters to do a single block of 10 AA - 1 per AA and 1 extra for whitespace).
4. Save the file and run it:
   ```bash
   python printProteinSequenceWithNumbering.py
   ```

### What you get

Text printed to your terminal that looks like this:

```
        10         20         30         40         50         60 
MRGSHHHHHH GSGEFLATTL ERIEKNFVIT DPRLPDNPII FASDSFLQLT EYSREEILGR 

        70         80         90        100        110        120 
NCRFLQGPET DRATVRKIRD AIDNQTEVTV QLINYTKSGK KFWNVFHLQP MRDYKGDVQY 

       130        140        150        160 
FIGVQLDGTE RLHGAAEREA VMLIKKTAFQ IAEAANDENY F
```

Copy and paste this into your document.

### Inputs

- No files needed. You just paste your sequence into the script.

### Dependencies

- None beyond Python itself.

---

## Process Spectra -- UV-Vis Spectrometer

**Script:** `processSpectra_uvVisSpectrometer.py`

**This is one of the two main spectra-processing scripts you will use day-to-day.** Use it when you have collected spectra on the benchtop UV-Vis spectrometer (the standalone instrument that produces `.SP` files).

### What it does

Reads in multiple `.SP` spectrum files from the UV-Vis spectrometer, sorts them by the timestamp embedded in each file, optionally zeros all spectra at a reference wavelength, and writes everything into a single tab-separated text file. The output is ready to open directly in Excel, Igor Pro, or any other plotting software.

### How to use it

1. Copy the script into the **same folder** as your `.SP` data files.
2. Open the script in a text editor and adjust two things:
   - **Line 82** -- `required_name_start`: change `"TIOL"` to whatever prefix your files share (e.g., `"DrBphP"` if your files are named `DrBphP_001.SP`, `DrBphP_002.SP`, etc.). If you want to read in every `.SP` file in the folder, set it to `""` (empty quotes).
   - **Line 96** -- `wavelengthToZeroAt`: the wavelength in nm at which to zero all spectra (default `550.0`). To skip zeroing, put a `#` at the start of line 99.
3. Save the script and run it from that folder:
   ```bash
   python processSpectra_uvVisSpectrometer.py
   ```

### What you get

A tab-separated `.txt` file named `<prefix>_allWavelengths.txt` (e.g., `DrBphP_allWavelengths.txt`). Its layout is:
- Row 1: source file names.
- Row 2: time of each spectrum in minutes, relative to the first spectrum.
- Remaining rows: one row per wavelength, with absorbance values across all spectra.

### Inputs

- `.SP` text files from the UV-Vis spectrometer, all in one folder.

### Dependencies

- `os` (standard library only -- no extra packages needed).

---

## Process Spectra -- Plate Reader (Single Cuvette Measurements)

**Script:** `processSpectra_plateReader_singleCuvetteMeasurements.py`

**This is the other main spectra-processing script.** Use it when you have used the plate reader in cuvette mode and exported each measurement as a separate `.TXT` file.

### What it does

Reads in multiple `.TXT` spectrum files exported from the plate reader (one file per cuvette measurement), sorts them by the timestamp in each file, optionally zeros at a reference wavelength, and combines them into one tab-separated output file. The output format is identical to the UV-Vis spectrometer script above.

### How to use it

1. Copy the script into the **same folder** as your `.TXT` data files.
2. Open the script in a text editor and adjust two things:
   - **Line 84** -- `required_name_start`: a filename prefix filter. By default this is `""`, which reads in all `.TXT` files in the folder. Change it to a specific prefix if you want to select only some files.
   - **Line 98** -- `wavelengthToZeroAt`: the zeroing wavelength in nm (default `550.0`). To skip zeroing, put a `#` at the start of line 101.
3. Save the script and run it from that folder:
   ```bash
   python processSpectra_plateReader_singleCuvetteMeasurements.py
   ```

### What you get

A tab-separated `.txt` file named `_allWavelengths.txt` (or `<prefix>_allWavelengths.txt` if you set a prefix). Same layout as described above: file names, timestamps, then absorbances by wavelength.

### Inputs

- `.TXT` files exported from the plate reader, one per measurement, all in one folder.

### Dependencies

- `os` (standard library only -- no extra packages needed).

---

## Other Spectra Scripts (Work in Progress)

**Folder:** `processSpectra_otherScripts/`

This folder contains two older plate reader scripts that have not yet been fully verified to work correctly. They are kept here for reference but are **not recommended for routine use** until they have been tested. Ask Max if you think you need one of them.

- **`processSpectra_plateReader_timeCourse.py`** -- intended for a single kinetic run where you exported multiple timepoint spectra as individual files. It extracts both the wall-clock timestamp and the time-since-experiment-start from each file and sorts by true elapsed time. (Note: the plate reader workflow that requires exporting spectra one at a time exists because exporting multiple spectra simultaneously can crash the plate reader software.)

- **`processSpectra_plateReader_timeCourse_individualSpectra.py`** -- an earlier version of the single-cuvette-measurements script. It may not parse the plate reader file format correctly for all software versions.

---

## Size Exclusion Chromatography Processing

**Script:** `sizeExclusionProcessing_goodCopy.py`

**Note:** This script was written for a specific older FPLC/SEC instrument setup. If you are using a different instrument or a newer software version, the file format may not match. Check that your data files look like what this script expects before using it, and ask a senior lab member for help if you are unsure.

### What it does

Reads FPLC (fast protein liquid chromatography) data files from a directory, applies a linear baseline correction between two user-specified elution volumes, aligns all runs to a common volume axis, and writes a combined tab-separated output file. It can also show an overlay plot of all the traces for quick visual inspection.

### How to use it

This script uses command-line arguments, so you control it entirely from the terminal:

```bash
python sizeExclusionProcessing_goodCopy.py \
  -i /path/to/your/data/folder \
  -o output.tsv \
  --baseline-start-vol 5.0 \
  --baseline-end-vol 10.0 \
  --xaxis volume
```

**Required arguments:**
- `-i` / `--input-dir`: path to a folder containing your FPLC text files.
- `-o` / `--output`: path for the output TSV file.

**Optional arguments:**
- `--baseline-start-vol`: start volume (mL) for baseline correction (default: `5.0`).
- `--baseline-end-vol`: end volume (mL) for baseline correction (default: `10.0`).
- `--xaxis`: choose `time` or `volume` for the x-axis of the QC plot (default: `time`).
- `--no-plot`: skip showing the plot entirely.

### What you get

- A tab-separated `.tsv` file with columns for each run and each detection channel (e.g., UV, QuadTec at various wavelengths, volume).
- A matplotlib plot window showing all the traces overlaid (unless `--no-plot` is used).

### Inputs

- A directory of FPLC text files. The script expects CSV-formatted files with a header row, optional QuadTec wavelength annotations, and numeric data columns.

### Dependencies

- `numpy`, `matplotlib`, `argparse`, `csv`, `re`, `os` (all included in the conda environment or standard library).

---

## Colour PDB by NMR Chemical Shift Perturbation

**Script:** `colour_pdb/recolour_protein_GA17_updated.py`

### What it does

A PyMOL script that colours residues in a protein structure according to their NMR chemical shift perturbation (CSP) data. Residues are classified into categories -- for example, residues that vanish upon ligand addition are coloured magenta, residues with large intensity decreases are blue, residues with large chemical shifts are green, unaffected assigned residues are yellow, and unassigned residues are white. It also shows C-alpha spheres on affected residues to make them easy to spot.

This was originally written for visualizing the effect of GA17 binding on the NpF2164g3 GAF domain, but it can be adapted for other proteins by changing the input files.

### How to use it

This script runs **inside PyMOL**, not from the regular command line.

1. Make sure the PDB file and the perturbation data file are in the **same directory** (see the `colour_pdb/` folder for examples).
2. Open **PyMOL**.
3. In the PyMOL command line (the text input at the bottom of the PyMOL window), navigate to the directory containing the script and data:
   ```
   cd /path/to/woolley_lab_tools/colour_pdb
   ```
4. Run the script:
   ```
   run recolour_protein_GA17_updated.py
   ```

Alternatively, you can use the PyMOL menu: File > Run Script, then select the `.py` file.

### Adapting it for your own protein

- **PDB file:** change the `pdbName` variable (line 8) to match your PDB file (without the `.pdb` extension).
- **Perturbation data file:** change the filename on line 15. The format is a simple two-column text file:
  - Column 1: residue number (integer).
  - Column 2: a code indicating the effect:
    - `0` = assigned but not affected (yellow).
    - `-1` = signal vanishes (magenta).
    - `-2` = large intensity decrease (blue).
    - `-3` = large chemical shift change (green).
  - The file must end with a line containing just `x` to signal end-of-file.
- **Residue range:** adjust the `np.arange(1,197)` on line 50 to match the number of residues in your protein.

### Inputs

- A `.pdb` file of your protein structure.
- A two-column text file with residue numbers and perturbation codes.

### Dependencies

- **PyMOL** (with its built-in Python). Also uses `numpy`, which may need to be installed within PyMOL's Python if it is not already present. In most recent PyMOL installations, numpy is included.

---

## Mass Spec Degraded Protein Identifier

**Script:** `massSpecDegradedProteinIndentifier/calc_degradation_goodCopy.py`

### What it does

When you observe unexpected peaks on a mass spectrum of your protein, this script helps you figure out what they are. Given a target mass and a protein sequence, it systematically trims residues from the N-terminus and C-terminus to find sub-sequences whose calculated mass matches the observed mass within a specified tolerance. It also accounts for cofactors/chromophores and nitrogen-15 isotope labelling.

### How to use it

1. Open `proteinSequence.txt` in the `massSpecDegradedProteinIndentifier/` folder and replace its contents with your protein's sequence (single-letter amino acid codes, one line, no spaces or headers).
2. Open `calc_degradation_goodCopy.py` and adjust these settings near the top of the file:
   - **`cofactorNetMass`** (lines 7-16): uncomment the line that matches your cofactor, or set a custom value. For a protein with no cofactor, use `0`. Note that biotinylation and some chromophore masses already subtract 18.02 Da for the water lost during conjugation -- make sure this is appropriate for your case.
   - **`massToFind`** (line 18): the observed mass (in Da) you are trying to identify.
   - **`N15_eff`** (line 19): set to `0.0` for unlabelled samples, or enter the labelling efficiency (e.g., `0.99`) for nitrogen-15 enriched samples. You can estimate this from the intact protein mass.
   - **`errorTolerance`** (line 20): how close (in Da) the calculated mass must be to `massToFind` to count as a match. Start with `1.0` for clean ESI data; try `3.0` or larger for noisier spectra.
3. Run from the `massSpecDegradedProteinIndentifier/` directory:
   ```bash
   cd massSpecDegradedProteinIndentifier
   python calc_degradation_goodCopy.py
   ```

### What you get

Terminal output showing:
- The calculated mass of the full (untruncated) protein.
- Two candidate identifications (one starting the search from the N-terminus, one from the C-terminus), each reporting: the matched mass, how many residues were lost from each end.

### Inputs

- `proteinSequence.txt`: your protein sequence (single-letter codes, one line).
- `residue_masses_numN.txt`: a reference table of amino acid residue masses and nitrogen counts. You should not need to edit this unless you are working with non-natural amino acids.

### Dependencies

- `numpy`.

---

## Process Multiple Thermal Reversion Traces for Tau

**Script:** `processMultipleThermalRevForTau/processMultipleThermalRevForTau.py`

### What it does

Fits a single-exponential recovery function to multiple kinetic (absorbance vs. time) traces and reports the time constant (tau) for each. This is commonly used to measure the thermal reversion half-life of photoswitchable proteins or azobenzene cross-linkers. The function fitted is:

```
A(t) = y0 - A * exp(-t / tau)
```

where tau is the time constant. The half-life is tau * ln(2).

### How to use it

1. Prepare your input data as a **tab-separated text file**:
   - The first column is time (in whatever units you prefer -- often seconds or minutes).
   - Every subsequent column is an absorbance trace (one column per replicate or sample).
   - **Important:** add a blank line at the very end of the file. The script uses this to know when to stop reading.
   - See `processMultipleThermalRevForTau_exampleInput.txt` for an example.
2. Open `processMultipleThermalRevForTau.py` and set the `fileName` variable on line 22 to your file's name (without the `.txt` extension).
3. Run from the `processMultipleThermalRevForTau/` directory:
   ```bash
   cd processMultipleThermalRevForTau
   python processMultipleThermalRevForTau.py
   ```
4. The script will show a plot of each trace with its fit overlaid. Close each plot window to advance to the next trace. (If you want to skip the plots, comment out the `plt.scatter`, `plt.plot`, and `plt.show()` lines.)

### What you get

- Interactive plots for visual inspection of each fit.
- The tau values for all traces printed to the terminal at the end. These are time constants, not half-lives -- multiply by ln(2) (approximately 0.693) to get the half-life.

### Fitting notes

The initial guesses for the curve fit are set on line 55: `p0=(0.1, 100, 0.1)`. If your fits are not converging, try adjusting these to values closer to what you expect for your system (amplitude, tau, and y-offset, respectively).

### Inputs

- A tab-separated text file with time in the first column and absorbance data in all other columns. Must end with a blank line.

### Dependencies

- `numpy`, `matplotlib`, `scipy`.

---

## Fill In CARA STR File (Advanced / Niche)

**Folder:** `fill_in_CARA_str/`

**Note:** This is a specialized tool for NMR spectroscopists who use the CARA software for resonance assignment. If you do not know what CARA is, you can safely skip this section. The code is somewhat experimental and may require manual adjustment for your specific project.

### What it does

When exporting chemical shift assignments from CARA, the built-in `WriteAssignments` script does not include shifts at the (i-1) position (i.e., C and CA shifts from the preceding residue in sequential assignment). This toolset works around that limitation:

1. A custom Lua script (`WriteAllSystemsAllSpins_PMMR.lua`) runs inside CARA to export **all** spins from all systems, including (i-1) position shifts.
2. A Python script (`gaf6_generate_modifiedStr.py`) then merges the (i-1) shifts into the `.str` file produced by CARA's standard `WriteAssignments` script.

### How to use it

See `explanation.txt` in the `fill_in_CARA_str/` folder for step-by-step instructions. In brief:

1. Import and run the Lua script inside CARA to get the full spin export.
2. Run CARA's built-in `WriteAssignments` to get the base `.str` file.
3. Run the Python script to merge the two. You will need to adjust the number of systems (line 41 of the Python script) and file names to match your project.

Some manual editing of the output may be needed to fill in residue identities at newly added (i-1) positions.

### Dependencies

- CARA NMR software (for the Lua script).
- Python (no extra packages beyond the standard library).

---

## Quick Reference: Which Script Do I Need?

| I want to...                                          | Use this script                                          |
|-------------------------------------------------------|----------------------------------------------------------|
| Print a protein sequence with residue numbering       | `printProteinSequenceWithNumbering.py`                   |
| Combine spectra from the benchtop UV-Vis spectrometer | `processSpectra_uvVisSpectrometer.py`                    |
| Combine plate reader spectra (cuvette measurements)   | `processSpectra_plateReader_singleCuvetteMeasurements.py` |
| Other plate reader workflows (unverified)             | `processSpectra_otherScripts/` (see section above)       |
| Process and baseline-correct SEC/FPLC data            | `sizeExclusionProcessing_goodCopy.py`                    |
| Colour a PDB structure by NMR perturbation data       | `colour_pdb/recolour_protein_GA17_updated.py` (in PyMOL) |
| Identify a degradation fragment from mass spec        | `massSpecDegradedProteinIndentifier/calc_degradation_goodCopy.py` |
| Fit thermal reversion kinetics for tau                | `processMultipleThermalRevForTau/processMultipleThermalRevForTau.py` |
| Patch CARA NMR shift export with (i-1) shifts         | `fill_in_CARA_str/` (see folder)                         |

---

## Questions or Problems?

If something does not work or you are not sure how to set up your input files, ask a senior lab member or reach out to Max.
