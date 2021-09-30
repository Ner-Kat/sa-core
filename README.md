# Steganalysis core

##### sa_core | ver. 1.2.1

***

### Decsription

This package contains different methods and functions for steganalysis. In includes methods for detecting LSB hiding and Koch-Zhao steganography in images.

***

### Requirements

Python interpreter ver. 3.3+

**Dependencies**: numpy, scipy, Pillow.

***

### Importing and structure

You can install package using PIP:

```
pip install sa_core-*.whl
```

Next you can import package:

```
import sa_core as sac
```

##### Main package classes and methods:

| type | name | description|
| :---: | :---: | :--- |
| class | ImageHandler | This class provides loading image by it path and needed for other package methods
| class | ChiSquareMethod | This class provides image analysis by ChiSquare method
| class | RegularSingularMethod | This class provides image analysis by Regular-Singular method
| class | KochZhaoAnalysisMethod | This class provides analysis of Koch-Zhao method that could be used for hiding in image
| class | **SaMethodHandler** | Steganalysis Methods Handler - this class provides a single handler of steganalysis for image (unite all steganalysis methods from the package). It is the most simple way to analyze steganography.
| structure | AnalyzerParams | This structure describes all parameters are needed for SaMethodHandler. You can pass this structure to SaMethodHandler (by `set` method) instead of specification all parameters manually (by `set_params` method).
| class | LsbHider | This class can be used for hiding the secret data into image by LSB steganography method
| class | LsbExtractor | This class can be used for extraction data that hidden into image by LSB steganography method
| class | KochZhaoHider | This class can be used for hiding the secret data into image by Koch-Zhao steganography method
| class | KochZhaoExtractor | This class can be used for extraction data that hidden into image by Koch-Zhao steganography method

##### Other

- Subpackage `sa_core.stego_module` contains more methods used for steganography of this package.
- Subpackage `sa_core.sa_math` contains some mathematical functions (like a DCT or a ChiSquare test).
- Subpackage `sa_core.sa_lib` contains some additional methods that are used by core.

If you imported sa_core, sa_math functions can be available like this:
```
import sa_core as sac
sac.math.dct()
```

If you imported sa_core, sa_lib functions can be available like this:
```
import sa_core as sac
sac.lib.read_bits_array()
```

***

### Usage example

```
# Imports
import sa_core as sac
import os.path


# Getting parameters values
...


# Creating and launching analyzer
params = sac.AnalyzerParams(img=path_to_some_img, do_chisqr=is_need_chi_sqr_analysis, do_rs=is_need_rs_analysis, do_kza=is_need_kz_analysis, chisqr_visualize=is_need_to_visualize_hidden_data, kza_extract=is_need_to_try_extract_data)
analyzer = sac.SaMethodsHandler()
analyzer.set(params)
results = analyzer.exec()


# Main results
chi_sqr_results = results.ChiSqrResult.fullness
rs_results = results.RsResult.volume
kza_results = results.KzaResult.volume


# Saving image array with visualized hidden data
imar = results.ChiSqrResult.visualized
img = sac.ImageHandler()
img.set_array(imar)

old_path = os.path.split(old_img_path)
new_img_path = old_path[0] + "_visualized_hidden_data" + old_path[1]
img.save(new_img_path)


# Print extracted data
print(results.KzaResult.data)


# Print additional information
print("Detected Koch-Zhao hiding threshold: {0}".format(results.KzaResult.threshold))

hidden_data_interval = results.KzaResult.indexes
print("Detected Koch-Zhao hidden data interval: {0}:{1}".format(*hidden_data_interval))
```
