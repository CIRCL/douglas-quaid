# Douglas-Quaid Project

Open source software for image correlation, distance and analysis.
Strongly related to : [Carl-Hauser](https://github.com/CIRCL/carl-hauser) 

# Problem statement (@CIRCL)

A lot of information collected or processed by CIRCL are related to images (at large from photos, screenshots of website or screenshots of sandboxes). The datasets become larger and analysts need to classify, search and correlate throught all the images. 

## Target

Building a generic library which can establish correlation between pictures, which can be easily integrated in [AIL](https://github.com/CIRCL/AIL-framework) and [MISP](https://github.com/MISP/MISP) (at least). Including a quick-lookup mechanism for correlation (similar to [ssdc](https://github.com/bwall/ssdc/blob/master/ssdc) techniques)

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
- Provide an algorithm-blind API : user should have nearly no choice for his requests. Parameters are server-side only.

Later : 
- Handling tags with storing picture : retrieve tags. This may be extended with any data.

## Getting Started

* Documentation of core components : [MarkDown - NOT UPDATED](./SOTA/Core_doc.md) | [PDF version](./SOTA/Core_doc.pdf)

### Questions

- **_Can the library say there is no match or will it always gives a "top N" matching pictures ?_**

For our automated usecases, e.g. MISP, we need clear "answer" from the library, to allow automation. 
The final goal of this library is to map all matches into one of the three categories : Accepted pictures, To-review pictures, and Rejected pictures.
Therefore, the goal will be to reduce the "to review" category to diminish needed human labor to edgy cases only.

- **_What is this library about ? Similarity search (global picture to picture matching) ? Object search (object detection in scene, followed by object search among other pictures) ? ..._**

For a first iteration, we are focusing on picture-to-picture matching. Therefore, given a bunch of already known pictures, we want to know which pictures - if any - are close to a request picture. This is similar to an inverted-search engine.

The library is mainly intended to work with screenshots like pictures. However, it may be tweaked to provide similar services in a different context.
However, matching principles are quite similar, and the extension may be trivial.

- **_Can I use the library in the current state for production ?_**

Yes. However, be aware that the current state of the library is "beta". Therefore, stability and performances may not be as high as you would expect for an industry-standard image-matching tool.
You can import the client API in your own Python software and perfom API calls to push picture/request search/pull results.

See [Client Example](https://github.com/CIRCL/douglas-quaid/blob/master/carlhauser_client/core.py) if you want to start.

### Prerequisites

See requirements.txt

(...)

### Installing

For server installation and client launch : See [installation instruction](./installation_info.md)

(...)

## Running the tests

(...)

## Behind the scene

Current library is a step behind [Carl-Hauser](https://github.com/CIRCL/carl-hauser) (:wink:) for algorithms implementation, but uses :
- ImageHash Algorithms (A-hash, P-hash, D-hash, W-hash ... )
- TLSH
- ORB

Performance (quality and time) is served by improvements and choices on top of these algorithms.

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

## Built With & Sources

* [Original project structure source](http://www.kennethreitz.org/essays/repository-structure-and-python)
* [Testing framework for algorithms](https://github.com/CIRCL/carl-hauser)
* [Followed practice for logging](https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/)
* [Text detector model source](https://github.com/argman/EAST)
* [Built-for-the-occasion manual image classificator](https://github.com/Vincent-CIRCL/visjs_classificator)
* [Bibliography](https://www.zotero.org/groups/2296751/carl-hauser/items)

## Contributing
PR are welcomed.
New issues are welcomed if you have ideas or usecase that could improve the project.
