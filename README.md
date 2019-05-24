# Carl-Hauser Project

Open source software for image correlation, distance and analysis.
 
# Problem statement (@CIRCL)

A lot of information collected or processed by CIRCL are related to images (at large from photos, screenshots of website or screenshots of sandboxes). The datasets become larger and analysts need to classify, search and correlate throught all the images. 

## Target

- Building a generic library and services which can be easily integrated in [AIL](https://github.com/CIRCL/AIL-framework) and [MISP](https://github.com/MISP/MISP) (at least). Including a quick-lookup mechanism for correlation (similar to [ssdc](https://github.com/bwall/ssdc/blob/master/ssdc) techniques)

Three main applications are envisioned : 
- Match new screenshots to a known baseline. E.g. : Matching screenshots from phishing-like website to known legitimate wesite.
- Match pictures or objects of pictures together. E.g : AIL; crawled websites (mainly Tor hidden services) from interpreted screenshot, 
- Match pictures or objects of pictures together. E.g : crawled websites or image extraction from DOM (ex : picture matching and inference if there is no text related to the picture.)


Other picture sources : 
- lookyloo screenshots from phishing-like - mix and non validated dataset
- screenshots from sandboxed malware analysis

## API Target

Now : 
- Provide a simple API : add pictures to the database, perform a picture-request 
- Provide an algorithm-blind API : user should have no choice except a threshold for his requests

Later : 
- Provide an extended API for post treatement : thresholding over the result / Storing request and asking results with many threshold
- Handling tags with storing picture : retrieve tags . Question : Extend it to any data store along with pictures ? 

## Getting Started

* Review of existing algorithms, techniques and libraries for calculating distances between images, State Of The Art : [MarkDown](./SOTA/SOTA.md) | [PDF version](./SOTA/SOTA.pdf)
* Documentation of core components : [MarkDown - NOT UPDATED](./SOTA/Core_doc.md) | [PDF version](./SOTA/Core_doc.pdf)

### Questions
- **_Do we want to a "YES they are the same"/"NO they're not" algorithms output, which can deliver an empty set of results (threeshold at some point) OR  do we want a "top N" algorithm, who's trying to match the best pictures he has ? (ranking algorithm)_**

Depends on the usecase. MISP would need a certain clear correlation for automation. The "best match" output is mainly useful for quality evaluation of different algorithms. However some application could use it as a production output.

The final goal of this library is to map all matches into one of the three categories : Accepted pictures, To-review pictures, and Rejected pictures.
Therefore, the goal will be to reduce the "to review" category to diminish needed human labor to edgy cases only.

- **_Is it about a similarity search (global picture matching) or an object search (1 object -> Where is it within a scene OR one Scene -> Many objects -> Where each object is within other Scene ?)_**

For a first iteration, we are focusing on picture-to-picture matching. Given problems we will face and usecases we will add, the project may be extended to object to picture matching.
However, matching principles are quite similar, and the extension may be trivial.

- **_Can I use the library in the current state for production ?_**

Not now. The library has for now no "core element" that you can atomically use in your own software. The library is for now mainly a testbench to evaluate algorithms on your own dataset.

### Prerequisites

See requirements.txt

(...)

### Installing

(...)

## Running the tests

(...)

## Running the benchmark evaluation

in /lib_testing you just have to launch "python3 ./launcher.py"
Parameters are hardcoded in the launcher.py, as : 
- Path to pictures folder
- Output folder to store results
- Requested outputs (result graphe, statistics, LaTeX export, threshold evaluation, similarity matrix ...)

This is currently working on most configuration and will explore following algorithms for matching : 
- ImageHash Algorithms (A-hash, P-hash, D-hash, W-hash ... )
- TLSH (be sure to have BMP pictures or uncompressed format at least. A function is available to convert pictures in /utility/manual.py) 
- ORB (and its parameters space)
- ORB Bag-Of-Words / Bag-Of-Features (and its parameters space, including size of the "Bag"/Dictionnary)
- ORB RANSAC (with/without homography matrix filtering)

You can also manually generate modified datasets from your original dataset : 
- Text detector and hider (DeepLearning, Tesseract, ...)
- Edge detector (DeepLearning, Canny, ...)
- PNG/BMP versions of pictures (compressed/uncompressed)

### For Developers

(...)


![Software architecture overview](./docs/images/overview-v1.svg)
More details are given in [Documentation PDF version](./SOTA/Core_doc.pdf)

<p  align="center" float="center">
<img src="./docs/images/action1.svg" alt="Action" height="100"/>
<img src="./docs/images/action2.svg" alt="Action" height="100"/>
<img src="./docs/images/datastruct.svg" alt="Example of datastructure stored for one picture in Redis storage instance" height="100"/>
<img src="./docs/images/principle1.svg" alt="Storage principle" height="100"/>
<img src="./docs/images/principle2.svg" alt="Storage principle, Idea vs Implementation" height="100"/>
<img src="./docs/images/principle3.svg" alt="Explanations" height="100"/>
<img src="./docs/images/queue1.svg" alt="How queues are working" height="100"/>
<img src="./docs/images/queue2.svg" alt="How queues are working" height="100"/>
</p>


## Deployment

(...)

For the algorithms test library : See [installation instruction](./installation_info.md)


## Built With & Sources

* [Original project structure source](http://www.kennethreitz.org/essays/repository-structure-and-python)
* [Followed practice for logging](https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/)
* [Text detector model source](https://github.com/argman/EAST)
* [Built-for-the-occasion manual image classificator](https://github.com/Vincent-CIRCL/visjs_classificator)
* [Bibliography](https://www.zotero.org/groups/2296751/carl-hauser/items)

## Contributing
PR are welcomed