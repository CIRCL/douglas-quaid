# Carl-Hauser Project

Open source software for image correlation, distance and analysis.
 
# Problem statement (@CIRCL)

A lot of information collected or processed by CIRCL are related to images (at large from photos, screenshots of website or screenshots of sandboxes). The datasets become larger and analysts need to classify, search and correlate throught all the images. 

## Target

- Building a generic library and services which can be easily integrated in [AIL](https://github.com/CIRCL/AIL-framework) and [MISP](https://github.com/MISP/MISP) (at least). Including a quick-lookup mechanism for correlation (similar to [ssdc](https://github.com/bwall/ssdc/blob/master/ssdc) techniques)

Three main applications are envisioned : 
- Match new screenshots to a known baseline. E.g. : Matching screenshots from phishing-like website to known legitimate wesite.
- Match pictures or objects of pictures together. E.g : AIL; crawled websites (mainly Tor hidden services) from interpreted screenshot, crawled websites - image extraction from DOM (ex : picture matching and inference if there is no text related to the picture.)


Other picture sources : 
- lookyloo screenshots from phishing-like - mix and non validated dataset
- screenshots from sandboxed malware analysis

## Getting Started

* Review existing algorithms, techniques and libraries for calculating distances between images, State Of The Art : [MarkDown](./SOTA/SOTA.md) | [PDF version](./SOTA/SOTA.pdf)

### Questions
- Do we want to a YES/NO algorithms output, which may not deliver any results, or do we want a "top N" algorithm, who's trying to match the best pictures he has ? 
First case require some kind of threeshold at some point. Second case is just a ranking algorithm.

Depends on the usecase. MISP would need a certain clear correlation for automation, whereas other application may only be a "best match" output.

- Is it a similarity search (global picture, then), an object search (1 object -> Where whitin a scene, OR one Scene -> Many objects -> Where each is within other Scene ?)

For a first iteration, we are focusing on picture-to-picture matching. Given problems we will face and usecases we will add, the project may be extended to object to picture matching.

### Prerequisites

(...)

### Installing

(...)

## Running the tests

(...)

### For Developers

(...)

## Deployment

(...)

## Built With & Sources

* [Original project structure source](http://www.kennethreitz.org/essays/repository-structure-and-python)
* [Built-for-the-occasion manual image classificator](https://github.com/Vincent-CIRCL/visjs_classificator)

## Contributing
