

# Kaiko API Oracle Feed

## Run locally
### Requirements
[Python3.7](https://realpython.com/installing-python/)

[Docker](https://docs.docker.com/install/)

PyTezos requires some libraries pre-installed. See [their quickstart](https://baking-bad.github.io/pytezos/#requirements) for instructions.

[Kaiko API Key](https://www.kaiko.com/)

### Install Python Requirements
Create a virtual python environment and activate it. 
```
? mkdir .env 
? python3 -m venv .env
? source .env/bin/activate

(.env) ? which pip 
/kaiko/.env/bin/pip
```

Now you can install requirements without polluting your global python dependencies.Use `source .env/bin activate` to activate the environment every time you want to use the repo locally. To leave the environment, use `deactivate`. 

```
(.env) ? pip install -r requirements.txt
```

### Environment Variables
Your environment variables file can be used both for running locally and for running docker. See `env-example`. Note that for docker to parse the variables correctly, you cannot have whitespace or quotes. 

Create one env file per feed.

### Running Tezos Sandbox

To run the Tezos Sandbox to develop and test locally, use `docker run -it -d -p 127.0.0.1:18731:18731 nomadiclabs/tezos-sandbox:py --time-between-blocks 7` and set `ENV=http://localhost:18731` in your env file.

## Oracle Contract 
The contract included in [`contract/oracle_contract.tz`](contract/oracle_contract.tz) stores values for each feed as a pair of timestamp and nat value. In [`api.py`](oracle/api.py), you can see how the results are parsed, and the price value is transformed into `nat`. Other contract storage types and supporting other transformations than just btc -> satoshi or usd -> cents can be done in this file.

This contract was created using [`lorentz-contract-oracle`](https://github.com/tqtezos/lorentz-contract-oracle)

```
$ stack exec -- lorentz-contract-oracle Oracle print --valueType "(pair timestamp nat)" --oneline
```

To create a contract on your local sandbox, you can use `lorentz-contract-oracle`, replacing \[bracketed values\] with your own:
```
$ tezos-client --wait none originate contract BTCXTZ transferring 0 from "[public key]" running "$(<[path/to/repo]/contract/oracle_contract.tz)\" --init "$(stack exec -- lorentz-contract-oracle Oracle init --initialValueType "(pair timestamp nat)" --initialValue "(Pair 0 0)" --admin \"[public key]\")" --burn-cap 0.712
```

Save the KT1 contract address generated in your env file as `ORACLE_ADDRESS=KT1...`

### Start Flask App

With env file created, you can start the flask app as follows:

```
(.env)$ export $(xargs <env)
(.env)$ flask run
```

The server should start, and you can make individual requests for oracle updates by hitting `localhost:5000`. A task that updates the oracle contract every 60 seconds with API data will also start. 

### Docker

Build

```bash
docker build -t kaiko-oracle:latest .
```

Run:

```bash
docker run -d -p 5000:5000 --env-file=[your-env-file] kaiko-oracle
```

Build and run:

```bash
docker build -t kaiko-oracle:latest . && docker run --rm -it -p 5000:5000 --env-file=[your-env-file] kaiko-oracle
```

For Mainnet deployments, you may want to think about using something more secure than environment variables for your secret keys. Docker swarm provides secrets that cannot be revealed inadvertently by logging the environment. https://docs.docker.com/engine/swarm/secrets/
