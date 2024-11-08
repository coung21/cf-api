mkdir -p ./model/checkpoints
wget -P ./model/checkpoints/ https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_small.pt
gdown 1B0Ipt5x3r_i7AnOpZeXA0CMpKPpiMloh -O model/checkpoints/cf_model.pt
gdown 1Xp-fxeOLvjR3j3bpEM4JDGgd4U9WCjnm -O model/checkpoints/unet-cf-2.pth