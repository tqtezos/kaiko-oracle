

## Run locally
### Requirements
[Python3.7](https://realpython.com/installing-python/)

[Docker](https://docs.docker.com/install/)

PyTezos requires some libraries pre-installed. See [their quickstart](https://baking-bad.github.io/pytezos/#requirements) for instructions.

### Install Python Requirements
Create a virtual python environment and activate it. 
```
? mkdir .env 
? python3 -m venv .env/kaiko-env
? source .env/kaiko-env/bin/activate

(kaiko-env) ? which pip 
/kaiko/.env/kaiko/bin/pip
```

Now you can install requirements without polluting your global python dependencies.Use `source .env/kaiko-env/bin activate` to activate the environment every time you want to use the repo locally. To leave the environment, use `deactivate`. 

```
(kaiko-env) ? pip install -r requirements.txt
```

### Environment Variables

## Oracle Contract 

For list of (identity, value)
```
$ stack exec -- lorentz-contract-oracle Oracle print --valueType "(list (pair string string))" --oneline
```

