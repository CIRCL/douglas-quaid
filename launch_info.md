### Full tutorial

Given you downloaded douglas-quaid and have a dataset where you want to find duplicates. 
You also have downloaded vis-js classificator and have a smaller dataset (subset or sample) which allows you to extract parameters.

Uniformization of files names. Using a "natural name hasher" available in the library.
> cd ./douglas-quaid/datasets/HumanHash
> python3 ./humanizer.py -p ./../raw_phishing_full

#### Server side
Perform douglas quaid first steps, if first launch
> Set the environement variable in the pipenv : CARLHAUSER_HOME=/home/user/Desktop/douglas-quaid

Set a "default" threshold for douglas-quaid and upload your pictures
In ./douglas-quaid/calrhauser_server/Configuration/distance_engine_conf.py you can modify 
this distance threshold to create a new cluster. Lesser the more cluster. Better to be lower than higher.
> self.MAX_DIST_FOR_NEW_CLUSTER = 0.2 

Launch douglas-quaid server
> pipenv run python3 ./douglas-quaid/carlhauser_server/core.py  

Check if the server is alive
> Access https://127.0.0.1:5000/ and you should get something like "The API is ALIVE"

Alternatively, you can also check it with cli :
> python3 douglas-quaid/carlhauser_client/API/cli.py ping

And you should get " {'Call_method': 'POST', 'Call_time': 'x', 'Called_function': 'ping', 'Status': 'The API is ALIVE :)'}"

#### Client side

Send all your picture and get the graph result. You can use a premade script ... 
> pipenv run python3 ./douglas-quaid/carlhauser_server/core.py

... or do it all by hand, with cli

Upload all the picture of your folder and create a (mapping file_name => server_side_id). Be aware that is overwrite the mapping file provided.
> pipenv run python3 ./API/cli.py upload -p ./../datasets/Pictures_folder -o ./mapping.json

```json
output : 
{
    "faint-aboriginal-unnatural-proof.png": "5d762064a5a5f885e1151503fe0eea9a9c5cfa64",
    "normal-abusive-cooing-profile.png": "57fdae199091d2fdeb7636780e2a3fb6096b225a",
    "future-ripe-cautious-reception.png": "3320a01d527da26c59bfd638e354fa2b5b65028e",
    "permissible-noiseless-macho-tough.png": "3e3273eae1f0452f58f63b62f98a0b9a4bd06d68",
    "resonant-ragged-sloppy-honey.png": "995f00a2bf37dbc6d27bf6182ec613464fff135c",
    "icky-amused-round-consideration.png": "40d9713dde3dcba80c09ade6817e997d8706ade4",
	(...)
```


Request similar picture of one of your pictures. You can specify the mapping file to get "real names" of pictures (client-side name).
> pipenv run python3 ./API/cli.py request -p ./../datasets/Other_folder/my_picture.png -o ./similar_pics.json -m ./mapping.json

```json
output : 
{
    "list_cluster": [
        {
            "cluster_id": "cluster|e633984b-aa02-44d4-8271-8bedd48bad55",
            "distance": 0.0
        }, (...)
    ],
    "list_pictures": [
        {
            "cluster_id": "cluster|e633984b-aa02-44d4-8271-8bedd48bad55",
            "distance": 0.0,
            "image_id": "lovely-absent-fat-brave.png"
        },
        {
            "cluster_id": "cluster|e633984b-aa02-44d4-8271-8bedd48bad55",
            "distance": 0.0026785714285714286,
            "image_id": "yielding-observant-tiresome-tea.png"
        }, (...)
    ],
    "request_id": "lovely-absent-fat-brave.png",
    "status": "matches_found",
    "request_time": 0.17814326286315918
}
```


Make a dump of the database as is of the server. You can specify the mapping file to get "real names" of pictures (client-side name). 
The -c option copy image's id in image's image field of nodes. Therefore, if path/filename are the ids, they can be displayed with visjs.
> pipenv run python3 ./API/cli.py dump -o ./dbdumpfile.json -m ./mapping.json -c

```json
output : 
{
    "meta": {
        "source": "DBDUMP"
    },
    "clusters": [
        {
            "label": "",
            "id": "cluster|d055eb40-5348-4937-8aeb-2f7ab74e9e0b",
            "image": "anchor.png",
            "shape": "icon",
            "members": [
                "murky-giddy-fancy-development.png",
                "gentle-exclusive-temporary-bath.png",
                "quixotic-smoggy-high-desk.png",
                "moaning-optimal-smoggy-vehicle.png",
                "strange-red-furtive-mixture.png"
            ],
            "group": ""
        }, (...)
    ],
    "nodes": [
        {
            "label": 0.42142857142857143,
            "id": "gentle-exclusive-temporary-bath.png",
            "image": "gentle-exclusive-temporary-bath.png",
            "shape": "image"
        },
        {
            "label": 0.43794642857142857,
            "id": "quixotic-smoggy-high-desk.png",
            "image": "quixotic-smoggy-high-desk.png",
            "shape": "image"
        }, (...)
    ],
    "edges": [
        {
            "from": "cluster|d055eb40-5348-4937-8aeb-2f7ab74e9e0b",
            "to": "gentle-exclusive-temporary-bath.png",
            "color": "gray"
        },
        {
            "from": "cluster|d055eb40-5348-4937-8aeb-2f7ab74e9e0b",
            "to": "quixotic-smoggy-high-desk.png",
            "color": "gray"
        }, (...)
    ]
}
```

See the mapping result in visjs classificator. You specify the picture folder, a temporary folder were a low-resolution version of pictures can be stored
and the database dump, previously saved.
> node server.js -i ./../douglas-quaid/datasets/Pictures_folder/ -t ./TMP -o ./TMP -j ./../douglas-quaid/carlhauser_client/dbdumpfile.json 


Creating a ground truth file
> cd visjs_classificator    
> node server.js -i ./../douglas-quaid/datasets/raw_phishing_full/ -t ./TMP -o ./TMP

Wait a few second before image reduction (improving display performance) and access : 
> localhost:3000