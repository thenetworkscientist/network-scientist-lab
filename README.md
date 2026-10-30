# The Network Scientist Lab

Small, honest simulations behind The Network Scientist's videos and Medium articles.
Each folder is one topic: the code reproduces every number we computed ourselves, with the assumptions written down.

| Topic | What it shows | Article |
|---|---|---|
| [Bullwhip effect](bullwhip-effect/) | Why a small sale makes factory orders swing almost 5x more than shoppers | [Read on Medium](https://medium.com/@TheNetworkScientist/why-the-factory-panics-when-you-barely-changed-your-shopping-cf6e3d40152e) | 
| [Newsvendor Problem](newsvendor/) | Why the best bakery plans for leftovers on 3 days out of 4, and how one ratio sets how much to bake | [Read on Medium](https://medium.com/@TheNetworkScientist/why-bakeries-bake-more-bread-than-they-can-sell-673226f1627d?postPublishedType=initial) |
| [Safety stock and risk pooling](safety-stock/) | Why one shared pool of spares needs far fewer than many private ones, and how linked bad days shrink the saving | [Read on Substack](https://thenetworkscientist.substack.com/p/why-sharing-spare-parts-beats-hoarding) |

## How to use any folder
```bash
cd <topic-folder>
pip install -r requirements.txt
python <script>.py
```

Questions or a result that looks off? Open an issue. Breaking the models is the point.

*The right question is always more valuable than the fastest answer.*

MIT licensed. The Network Scientist.
