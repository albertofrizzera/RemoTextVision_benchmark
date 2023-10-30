<center> 
<h1><strong>satellite-CLIP-benchmarks</strong></h1>
<em>
Alberto Frizzera, info@albertofrizzera.com<br>
Riccardo Ricci
</em>
<br>
</center>

This project aims at developing a platform for benchmarking your finetuned CLIP with the most popular satellite datasets.

## Installation

1. Create a conda environment following the instructions contained in ```env_linux.txt```.
2. Adjust the environmental variables of the dataset in ```.env```.

## Benchmark Datasets

The following list provides the datasets used to benchmark your model.

### Zero shot classification
- [X] [BigEarthNet](https://bigearth.net)
- [X] [EuroSAT](https://github.com/phelber/eurosat)
- [X] [MLRSNet](https://github.com/cugbrs/MLRSNet)
- [X] [NWPU](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwi04IL9q82BAxVf2QIHHcdZB2IQFnoECBEQAQ&url=https%3A%2F%2Fieeexplore.ieee.org%2Fdocument%2F9866055%2F&usg=AOvVaw1JwAV33hy2u01BafEGSI0P&opi=89978449)
- [X] [OPTIMAL_31](https://huggingface.co/datasets/jonathan-roberts1/Optimal-31)
- [X] [PatternNet](https://sites.google.com/view/zhouwx/dataset)
- [ ] [RSI_CB128](https://github.com/lehaifeng/RSI-CB)
- [X] [RSI_CB256](https://github.com/lehaifeng/RSI-CB)
- [X] [RESISC45](https://figshare.com/articles/dataset/NWPU-RESISC45_Dataset_with_12_classes/16674166)
- [ ] [RS2800]()
- [ ] [RSC11]()
- [ ] [RSSCN7]()
- [X] [RSICD](https://github.com/201528014227051/RSICD_optimal)
- [X] [RSITMD](https://github.com/xiaoyuan1996/AMFMN)
- [X] [SIRI_WHU](http://www.lmars.whu.edu.cn/prof_web/zhongyanfei/e-code.html)
- [X] [UCM](http://weegee.vision.ucmerced.edu/datasets/landuse.html)
- [ ] [AID](https://captain-whu.github.io/AID/)
- [X] [WHU_RS19](https://captain-whu.github.io/BED4RS/#)

### Image retrieval
- [X] [NWPU](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwi04IL9q82BAxVf2QIHHcdZB2IQFnoECBEQAQ&url=https%3A%2F%2Fieeexplore.ieee.org%2Fdocument%2F9866055%2F&usg=AOvVaw1JwAV33hy2u01BafEGSI0P&opi=89978449)
- [X] [RSICD](https://github.com/201528014227051/RSICD_optimal)
- [X] [RSITMD](https://github.com/xiaoyuan1996/AMFMN)
- [X] [SIDNEY](https://mega.nz/folder/pG4yTYYA#4c4buNFLibryZnlujsrwEQ)
- [X] [UCM](https://mega.nz/folder/wCpSzSoS#RXzIlrv--TDt3ENZdKN8JA)

Datasets marked with [X] are already implemented and ready to use.  

We are constantly updating the number of dataset that we support for testing. 
If needed, an exhaustive list of other satellite datasets is available [here](https://captain-whu.github.io/DiRS/).

To visualize the samples of all the above datasets, a web tool has been implemented (```web_app/main.py```)