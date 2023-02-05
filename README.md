bitcoin majority hashrate attack simulation
===========================================
Program to simulate a 51%-attack. It simulates the proceeding of the two blockchains (majority and minority) in parallel.

[![asciicast](https://asciinema.org/a/555310.svg)](https://asciinema.org/a/555310)

From investopedia.com:

 > What Is a 51% Attack?
 >
 >A 51% attack is an attack on a cryptocurrency blockchain by a group of miners who control more than 50% of the network's mining hash rate. Owning 51% of the nodes on the network gives the controlling parties the power to alter the blockchain. 


**For deeper understandig read Joe Kellys excellent article series:
https://joekelly100.medium.com/on-bitcoins-fee-based-security-model-part-1-beware-the-turkey-fallacy-4285e18d41ea**

Requirements & Installation
---------------------------
 - Requirement: poetry - for setting up the environment - https://python-poetry.org/
 - Installation:
   - Checkout source
   - run `poetry update && poetry install` in project folder.


Getting started
---------------
Run with default hashrate and block threshold:

    poetry run python btc_mining_simulation/mining-controller.py       
    MiningController
    Total Hashrate 1000/s Majority 510.0/s Minority 490.0/s

Usage
-----
    BTC Mining Simulation Controller [-h] [-mhr MAJORITY_HASHRATE_PERCENT] [-hr HASHRATE] [-thr HASH_THRESHOLD]

    options:
    -h, --help            show this help message and exit
    -mhr MAJORITY_HASHRATE_PERCENT, --majority-hashrate-percent MAJORITY_HASHRATE_PERCENT
                            How big is the fraction of the majority hashrate? Default '0.51' equates to 51 percent
    -hr HASHRATE, --hashrate HASHRATE
                            Total hashrate per s. Default 1000
    -thr HASH_THRESHOLD, --hash-threshold HASH_THRESHOLD
                            Max hash value in HEX (4 Bytes). Default '00AFFFFF'

Architecture
------------
The program consists of three processes. The Controller and two mining agents.
The purpose of using different processes is to show that the mining of the majority miner and the rest of the miners (minority) is completely decoupled. It also prevents any influence of the GIL.

The mining agents communicate with the controller by using stdout and stdin.
When a block is found by a mining agent. It reports to the controller which paints the progressbars and does the output.

    ┌────────────────────────────────────────┐
    │                                        │
    │                                        │
    │           Mining Controller            │
    │                                        │
    │                                        │
    └──────▲─┬───────────────────────▲─┬─────┘
           │ │                       │ │
           │ │                       │ │
           │ │                       │ │
    ┌──────┴─▼─────┐         ┌───────┴─▼─────┐
    │              │         │               │
    │ Mjority Hash │         │ Minority Hash │
    │              │         │               │
    │    Agent     │         │     Agent     │
    │              │         │               │
    └──────────────┘         └───────────────┘