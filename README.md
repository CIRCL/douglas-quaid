# Douglas-Quaid Project

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/e27a772481ed4033861670b9767249b6)](https://app.codacy.com/app/zettacircl/douglas-quaid?utm_source=github.com&utm_medium=referral&utm_content=Vincent-CIRCL/douglas-quaid&utm_campaign=Badge_Grade_Dashboard)

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

### Installing

For server and client, installation and launch : See [detailed installation instruction](./installation_info.md)  

### TLDR ; I want it to work ! 
Please follow 'detailed installation instruction' if you meet any issue.

###### Installation : 

```bash
pipenv install
pipenv shell  
chmod +x ./tlsh_install.sh    
sudo ./tlsh_install.sh     
sudo apt-get install redis
```

###### Server side launch : 

```bash
cd ./carlhauser_server
pipenv run python3 ./core.py   
```

###### Client side launch : 
All approaches are equivalents. Pick the one that suits you the most.

```bash
cd ./carlhauser_client
pipenv run python3 ./core.py  
```

or via CLI 

```bash
pipenv shell

# Upload all pictures of folder "Pictures_folder" and create a mapping (file_name => server_side_id)
python3 ./API/cli.py upload -p ./../datasets/Pictures_folder -o ./mapping.json

# Request similar picture of one of your pictures. You can specify the mapping file to get "real names" of pictures (client-side name).
python3 ./API/cli.py request -p ./../datasets/Other_folder/my_picture.png -o ./similar_pics.json -m ./mapping.json

# Make a dump of the database as is of the server. You can specify the mapping file to get "real names" of pictures (client-side name). 
python3 ./API/cli.py dump -o ./dbdumpfile.json -m ./mapping.json -c
```

or from your own custom python file

```python
import pathlib
from carlhauser_client.Helpers.environment_variable import get_homedir
from carlhauser_client.API.simple_api import Simple_API

# Generate the API access point link to the hardcoded server
cert = (get_homedir() / "carlhauser_client" / "cert.pem").resolve()
api = Simple_API(url='https://localhost:5000/', certificate_path=cert)

# Each call to API return 2 values. 
# First value = success boolean, Second value = json response of the server

# Ping server (sanity check, not technicaly required) 
api.ping_server()

# perform uploads
api.add_picture_server(get_homedir() / "datasets" / "simple_pictures" / "image.jpg")
# (...)

# Request a picture matches
request_id = api.request_picture_server(get_homedir() / "datasets" / "simple_pictures" / "image.bmp")[1]
# (...)

# Wait a bit
api.poll_until_result_ready(request_id, max_time=60)

# Retrieve results of the previous request (print on screen)
results = api.retrieve_request_results(request_id)[1]

# Triggers a DB export of the server as-is, to be displayed with visjsclassificator. Server-side only operation.
api.export_db_server()
```

or from extended API
```python
import pathlib
from carlhauser_client.Helpers.environment_variable import get_homedir
from carlhauser_client.API.extended_api import Extended_API

# Generate the API access point link to the hardcoded server
cert = (get_homedir() / "carlhauser_client" / "cert.pem").resolve()
api = Extended_API(url='https://localhost:5000/', certificate_path=cert)

# Ping server (sanity check, not technicaly required) 
api.ping_server()

# perform uploads
api.add_pictures_to_db(get_homedir() / "datasets" / "simple_pictures")

# Retrieve results of the previous request (print on screen)
results = api.request_similar_and_wait(get_homedir() / "datasets" / "simple_pictures" / "image.bmp")

# Triggers a DB export of the server as-is, to be displayed with visjsclassificator. Server-side only operation.
db_dump = api.get_db_dump_as_graph()
```

### Prerequisites

See requirements.txt

(...)

## Running the tests

(...)

## Behind the scene

Current library is a step behind [Carl-Hauser](https://github.com/CIRCL/carl-hauser) (:wink:) for algorithms implementation, but uses :
- ImageHash Algorithms (A-hash, P-hash, D-hash, W-hash ... )
- TLSH
- ORB

Performance (quality and time) is served by improvements and design choices on top of these algorithms.

## Configuration and Tweaking

#### Must known

The library is storing pictures within clusters of somewhat-similar pictures. 
When a picture is added in the database or a request is made, algorithms perform a comparison of the picture with all "most central"/"most representative" picture(s) of each cluster.  
Therefore, instead of making a comparison of one pictures to all pictures of the database (O(nb_picture_in_db)), it compares the picture with all clusters (O(nb_clusters)).    
Depending on a threshold, the picture will be matched to a cluster (in fact, the representative picture of the cluster) or not. If the picture match a representative picture of a cluster, we compare the request picture with all pictures of this cluster.   
Therefore, instead of running O(nb_picture_in_db) comparisons, we run O(nb_clusters + nb_matched_clusters*nb_pictures_in_each_cluster)  
This improves performances by decreasing performed comparisons.

Tricky thing is the threshold which says "This picture is too distant, it must be in a new cluster" or "This picture is close enough and is in the same cluster"*[]: 
This threshold impacts on the performance of the library (time-wise) and less/not on the quality of match.

<p  align="center" float="center">
<img src="./docs/images/xkcd_performance.png" alt="Action" height="500"/>
<br/>
How you must understand this "new cluster threshold".
</p>


However, one consequence and must-known is : ** this threshold should be set once and for all at server start.** All the performance-datastructures are built on top of it. It must be consistent between adding-time and request-time. Unexpected results will occur otherwise.   
Moreover you can't make a "wrong choice" for this threshold. At worst, it will be slow, but it will work.

I repeat : 
<h2>

```diff
- **'MAX_DIST_FOR_NEW_CLUSTER' threshold should be set once and for all at server start.**
```

</h2>


If the threshold is 1 : all pictures will be in one big cluster, so the library will always match "this cluster" and so all pictures will be compared two-by-two. (Fallback to O(nb_picture_in_db))
If the threshold is 0 : each pictures will be in its own cluster, so the library will compare all "head of clusters" and so all pictures will be compared two-by-two. (Fallback to O(nb_picture_in_db))
Anything in the middle will improve performance.

Empirically, 0.2 was not a bad value. Evaluation algorithms are available if you want to get True-Positive/False-Positive/True-Negative/False-Negative/Acc/F1 measures depending on this threshold.

#### Parameters tweaking

The library has many parameters. To correctly configure the library for your own usecase, you may have to tweak these values. Therefore, you must understand them.  

Each algorithm computes distance between pictures. Each algorithm has it's own way to compute this distance, but all outputs a value within range  \[0-1\].  Example : A-HASH outputs a distance of 0.4 between picture A and B
Each algorithm computes a decision about two pictures comparison. Thresholds over its own distance calculation give a YES/MAYBE/NO decision.    Example : A-HASH outputs a decision "YES (it matches)" between picture A and B, because distance between picture A and B is 0.4, which is less than the "Maybe_threshold" of A-HASH. 

During two pictures comparison, configured algorithms are called. Each provides a distance and a decision.  
A merging algorithm do merge these distances and do merge these decisions.  
Distances can be merged with distinct approaches : max of all distances, mean of all distances, min of all distances, harmonic mean, weighted mean of all distances, etc.
Decisions can be merged with distinct approaches : a Pareto rule (if 80% algorithms give the same decision, we output this decision), majority rule (most prevalent decision is returned), weighted majority, pyramidal (we check for high some algorithms, and if unsure, we check others)



#### Performance optimization process

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
