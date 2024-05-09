# -------------------------------------------------------------------------
# Author:   Alberto Frizzera, info@albertofrizzera.com
# Date:     12/10/2023
# -------------------------------------------------------------------------

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "."))
import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from pdflatex import PDFLaTeX
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from torchvision.transforms import InterpolationMode
BICUBIC = InterpolationMode.BICUBIC
import torch 
import open_clip
import torch.utils.data as dutils
from typing import List
from transformers import CLIPProcessor, CLIPModel, CLIPImageProcessor, CLIPTokenizer
from tqdm import tqdm
import PIL

def time_convert(seconds):
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)


def draw_results_table(df, alignment="c", df_baseline=None):
    if np.any(df):
        columns = pd.Series(df.columns.values).apply(lambda x: "\\rotatebox[origin=c]{90}{ \\textbf{"+x.replace("_","\_")+"} }")
        latex_table = "\\begin{tabular}{"+alignment*len(columns)+"""}
\hline
\hline
\\rowcolor[rgb]{0.835,0.835,0.835} """+" & ".join(columns)+""" \\\\"""
        if np.any(df_baseline):
            latex_table += """
\hline
\\rowcolor[rgb]{0.76,0.88,1} """+"\\n".join(df_baseline.iloc[0:1].to_latex(float_format="%.4f", index=False, header=False).split("\n")[3:-3])+"""
\hline
\\rowcolor[rgb]{0.84,1,0.82} """+"\\n".join(df_baseline.iloc[1:2].to_latex(float_format="%.4f", index=False, header=False).split("\n")[3:-3])+"""
\hline
\\rowcolor[rgb]{0.95,0.93,0.74} """+"\\n".join(df_baseline.iloc[2:3].to_latex(float_format="%.4f", index=False, header=False).split("\n")[3:-3])
        latex_table += """
\hline
"""+"\\n".join(df.to_latex(float_format="%.4f", index=False, header=False).split("\n")[3:-3])+"""
\hline
\hline
\end{tabular}
"""
        return latex_table
    else:
        return ""


def draw_params_table(params):
    df = pd.DataFrame([{"\\textbf{"+key.replace("_","\_")+"}": str(params[key]) for key in params.keys()}]).T
    df[0] = df[0].apply(lambda x: x.replace("_","\_"))
    latex_table = """\\begin{tabularx}{\columnwidth}{r|X}
"""+"\n".join(df.to_latex(header=False).split("\n")[3:-3])+"""
\end{tabularx}
"""
    return latex_table


def build_report(params, report_log, datetime, include_baseline=False):
    if "zero_shot" in report_log["dataset_type"].values:
        zero_shot_ids = np.where(report_log["dataset_type"]=="zero_shot")
        zero_shot_table = pd.DataFrame(columns=report_log.loc[zero_shot_ids]["dataset_name"].values)
        zero_shot_table.loc[0] = report_log.loc[zero_shot_ids]["accuracy"].values
    else:
        zero_shot_table = None
    
    if "lnr_prob" in report_log["dataset_type"].values:
        lnr_prob_ids = np.where(report_log["dataset_type"]=="lnr_prob")
        lnr_prob_table = pd.DataFrame(columns=report_log.loc[lnr_prob_ids]["dataset_name"].values)
        lnr_prob_table.loc[0] = report_log.loc[lnr_prob_ids]["accuracy"].values
    else:
        lnr_prob_table = None
    
    if "knn" in report_log["dataset_type"].values:
        knn_ids = np.where(report_log["dataset_type"]=="knn")
        knn_table = pd.DataFrame(columns=report_log.loc[knn_ids]["dataset_name"].values)
        knn_table.loc[0] = report_log.loc[knn_ids]["accuracy"].values
    else:
        knn_table = None
    
    if "image2text" in report_log["dataset_type"].values:
        image2text_ids = np.where(report_log["dataset_type"]=="image2text")
        image2text_table = pd.DataFrame(columns=report_log.loc[image2text_ids]["dataset_name"].values)
        image2text_table.loc[0] = report_log.loc[image2text_ids]["accuracy"].values
    else:
        image2text_table = None
    
    if "text2image" in report_log["dataset_type"].values:
        text2image_ids = np.where(report_log["dataset_type"]=="text2image")
        text2image_table = pd.DataFrame(columns=report_log.loc[text2image_ids]["dataset_name"].values)
        text2image_table.loc[0] = report_log.loc[text2image_ids]["accuracy"].values
    else:
        text2image_table = None
    
    if include_baseline:
        report_log_CLIP_baseline = pd.read_csv(open(os.path.join(os.path.dirname(__file__),"reports","CLIP_baseline","report_CLIP_baseline.csv"), "rb"), index_col=0)
        report_log_CLIP_rsicd_v2_baseline = pd.read_csv(open(os.path.join(os.path.dirname(__file__),"reports","CLIP_rsicd_v2_baseline","report_CLIP_rsicd_v2_baseline.csv"), "rb"), index_col=0)
        report_log_RemoteCLIP_baseline = pd.read_csv(open(os.path.join(os.path.dirname(__file__),"reports","RemoteCLIP_baseline","report_RemoteCLIP_baseline.csv"), "rb"), index_col=0)
        
        report_log_CLIP_baseline = report_log_CLIP_baseline[report_log_CLIP_baseline["dataset_name"].isin(report_log["dataset_name"].values)].reset_index(drop=True)
        report_log_CLIP_rsicd_v2_baseline = report_log_CLIP_rsicd_v2_baseline[report_log_CLIP_rsicd_v2_baseline["dataset_name"].isin(report_log["dataset_name"].values)].reset_index(drop=True)
        report_log_RemoteCLIP_baseline = report_log_RemoteCLIP_baseline[report_log_RemoteCLIP_baseline["dataset_name"].isin(report_log["dataset_name"].values)].reset_index(drop=True)
        
        assert np.all(report_log_CLIP_baseline["dataset_name"]==report_log_CLIP_rsicd_v2_baseline["dataset_name"]) and np.all(report_log_CLIP_baseline["dataset_name"]==report_log_RemoteCLIP_baseline["dataset_name"]), "Error! Mismatch of the available datasets of the baseline models."
        if "zero_shot" in report_log["dataset_type"].values:
            zero_shot_ids = np.where(report_log_CLIP_baseline["dataset_type"]=="zero_shot")
            zero_shot_table_baseline = pd.DataFrame(columns=report_log_CLIP_baseline.loc[zero_shot_ids]["dataset_name"].values)
            zero_shot_table_baseline.loc[0] = report_log_CLIP_baseline.loc[zero_shot_ids]["accuracy"].values
            zero_shot_table_baseline.loc[1] = report_log_CLIP_rsicd_v2_baseline.loc[zero_shot_ids]["accuracy"].values
            zero_shot_table_baseline.loc[2] = report_log_RemoteCLIP_baseline.loc[zero_shot_ids]["accuracy"].values
        else:
            zero_shot_table_baseline = None
        
        if "lnr_prob" in report_log["dataset_type"].values:
            lnr_prob_ids = np.where(report_log_CLIP_baseline["dataset_type"]=="lnr_prob")
            lnr_prob_table_baseline = pd.DataFrame(columns=report_log_CLIP_baseline.loc[lnr_prob_ids]["dataset_name"].values)
            lnr_prob_table_baseline.loc[0] = report_log_CLIP_baseline.loc[lnr_prob_ids]["accuracy"].values
            lnr_prob_table_baseline.loc[1] = report_log_CLIP_rsicd_v2_baseline.loc[lnr_prob_ids]["accuracy"].values
            lnr_prob_table_baseline.loc[2] = report_log_RemoteCLIP_baseline.loc[lnr_prob_ids]["accuracy"].values
        else:
            lnr_prob_table_baseline = None
        
        if "knn" in report_log["dataset_type"].values:
            knn_ids = np.where(report_log_CLIP_baseline["dataset_type"]=="knn")
            knn_table_baseline = pd.DataFrame(columns=report_log_CLIP_baseline.loc[knn_ids]["dataset_name"].values)
            knn_table_baseline.loc[0] = report_log_CLIP_baseline.loc[knn_ids]["accuracy"].values
            knn_table_baseline.loc[1] = report_log_CLIP_rsicd_v2_baseline.loc[knn_ids]["accuracy"].values
            knn_table_baseline.loc[2] = report_log_RemoteCLIP_baseline.loc[knn_ids]["accuracy"].values
        else:
            knn_table_baseline = None
        
        if "image2text" in report_log["dataset_type"].values:
            image2text_ids = np.where(report_log_CLIP_baseline["dataset_type"]=="image2text")
            image2text_table_baseline = pd.DataFrame(columns=report_log_CLIP_baseline.loc[image2text_ids]["dataset_name"].values)
            image2text_table_baseline.loc[0] = report_log_CLIP_baseline.loc[image2text_ids]["accuracy"].values
            image2text_table_baseline.loc[1] = report_log_CLIP_rsicd_v2_baseline.loc[image2text_ids]["accuracy"].values
            image2text_table_baseline.loc[2] = report_log_RemoteCLIP_baseline.loc[image2text_ids]["accuracy"].values
        else:
            image2text_table_baseline = None
        
        if "text2image" in report_log["dataset_type"].values:
            text2image_ids = np.where(report_log_CLIP_baseline["dataset_type"]=="text2image")
            text2image_table_baseline = pd.DataFrame(columns=report_log_CLIP_baseline.loc[text2image_ids]["dataset_name"].values)
            text2image_table_baseline.loc[0] = report_log_CLIP_baseline.loc[text2image_ids]["accuracy"].values
            text2image_table_baseline.loc[1] = report_log_CLIP_rsicd_v2_baseline.loc[text2image_ids]["accuracy"].values
            text2image_table_baseline.loc[2] = report_log_RemoteCLIP_baseline.loc[text2image_ids]["accuracy"].values
        else:
            text2image_table_baseline = None
        baseline_legend = "\\noindent \n The baselines refer to the models: \colorbox{CLIPcolor}{\\textbf{CLIP}}, \colorbox{CLIPrsicdColor}{\\textbf{CLIP\_rsicd\_v2}} and \colorbox{RemoteCLIP}{\\textbf{RemoteCLIP}}."
    else:
        zero_shot_table_baseline = None
        lnr_prob_table_baseline = None
        knn_table_baseline = None
        image2text_table_baseline = None
        text2image_table_baseline = None
        baseline_legend = ""
    
    environment = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),"templates/")))
    template = environment.get_template("report.txt")
    context = {
        "datetime" : datetime.replace("_","\_"),
        "baseline_legend": baseline_legend,
        "model_table" : draw_params_table(params),
        "zero_shot_table" : draw_results_table(zero_shot_table, df_baseline=zero_shot_table_baseline),
        "lnr_prob_table" : draw_results_table(lnr_prob_table, df_baseline=lnr_prob_table_baseline),
        "knn_table" : draw_results_table(knn_table, df_baseline=knn_table_baseline),
        "image2text_table" : draw_results_table(image2text_table, df_baseline=image2text_table_baseline),
        "text2image_table" : draw_results_table(text2image_table, df_baseline=text2image_table_baseline)}
    if sys.platform == "linux" or sys.platform == "darwin":
        renderer_template = template.render(context).replace('\n','\r\n')
    else:
        renderer_template = template.render(context)
    with open(os.path.join(os.path.dirname(__file__),"reports",datetime,"report_"+datetime+".tex"), mode="w", encoding="utf-8") as results:
        results.write(renderer_template)
    pdfl = PDFLaTeX.from_texfile(os.path.join(os.path.dirname(__file__),"reports",datetime,"report_"+datetime+".tex"))
    pdf, log, completed_process = pdfl.create_pdf(keep_pdf_file=False, keep_log_file=False)
    with open(os.path.join(os.path.dirname(__file__),"reports",datetime,"report_"+datetime+".pdf"), 'wb') as f:
        f.write(pdf)
    with open(os.path.join(os.path.dirname(__file__),"reports",datetime,"report_"+datetime+".log"), 'wb') as f:
        f.write(log)


def parse_line_args(args, params): 
    if args.RUN_ID:
        params["model_checkpoints"]["RUN_ID"] = args.RUN_ID
    if args.RUN_epoch:
        params["model_checkpoints"]["epoch"] = args.RUN_epoch
    return params

# BRUTALLY COPIED FROM @zzbuzzard https://github.com/openai/CLIP/issues/115

# Encodes all text and images in a dataset
def encode_dataset(model, dataset: dutils.Dataset, encode_text_fn:callable, encode_img_fn:callable, batch_size:int = 16, device:str = "cuda"):
    with torch.no_grad():
        # image_to_text_map[i] gives the corresponding text indices for the ith image
        #  (as there are multiple pieces of text for each image)
        image_to_text_map = []
        
        # text_to_image_map[i] gives the corresponding image index for the ith text
        text_to_image_map = []

        dataloader = dutils.DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=8, pin_memory=True)

        image_encodings = []
        text_encodings = []

        text_index = 0
        image_index = 0

        for images, text in tqdm(dataloader):
            
            text_features = encode_text_fn(model=model, texts=texts, device=device)
            # Normalize them
            text_features /= text_features.norm(dim=1, keepdim=True)

            # text has shape B x 5 x 77
            batch_size, captions_per_image, _ = text_features.shape

            # Update text_to_image_map and image_to_text_map for this batch
            for i in range(batch_size):
                # the next image corresponds to text captions [text_index ... text_index + captions_per_image - 1]
                text_indices = list(range(text_index, text_index + captions_per_image))
                image_to_text_map.append(text_indices)
                text_index += captions_per_image

                # Each of the next captions_per_image text captions correspond to the same image
                text_to_image_map += [image_index] * captions_per_image
                image_index += 1

            # B x 5 x 77 -> (B*5) x 77
            text = torch.flatten(text, start_dim=0, end_dim=1)
            
            image_encodings.append(model.encode_image(images))
            text_encodings.append(model.encode_text(text))

        image_encodings = torch.cat(image_encodings)
        text_encodings = torch.cat(text_encodings)
        text_to_image_map = torch.LongTensor(text_to_image_map).to(device)
        image_to_text_map = torch.LongTensor(image_to_text_map).to(device)

        # Normalise encodings
        image_encodings = image_encodings / image_encodings.norm(dim=-1, keepdim=True)
        text_encodings = text_encodings / text_encodings.norm(dim=-1, keepdim=True)

        return image_encodings, text_encodings, text_to_image_map, image_to_text_map


def recall_at_k(model, dataset: dutils.Dataset, encode_text_fn:callable, encode_img_fn:callable, k_vals: List[int], batch_size:int, device:str = "cuda"):
    print("Encoding all data...")
    image_encodings, text_encodings, text_to_image_map, image_to_text_map = encode_dataset(model, dataset, batch_size=batch_size, device=device)
 
    num_text = text_encodings.shape[0]
    num_im = image_encodings.shape[0]
    captions_per_image = image_to_text_map.shape[1]

    # text-to-image recall
    print("Text-to-image recall...")

    dist_matrix = text_encodings @ image_encodings.T  # dist_matrix[i] gives logits for ith text

    # Note: this matrix is pretty big (25000 x 5000 with dtype float16 = 250MB)
    #  torch.argsort runs out of memory for me (6GB VRAM) so I move to CPU for sorting
    dist_matrix = dist_matrix.cpu()

    # Sort in descending order; first is the biggest logit
    inds = torch.argsort(dist_matrix, dim=1, descending=True)
    inds = inds.to(device)

    text_to_image_recall = []

    for k in k_vals:
        # Extract top k indices only
        topk = inds[:, :k]

        # Correct iff one of the top_k values equals the correct image (as given by text_to_image_map)
        correct = torch.eq(topk, text_to_image_map.unsqueeze(-1)).any(dim=1)

        num_correct = correct.sum().item()
        text_to_image_recall.append(num_correct / num_text)


    # image-to-text recall
    print("Image-to-text recall...")
    dist_matrix = dist_matrix.T  # dist_matrix[i] gives logits for the ith image

    # Sort in descending order; first is the biggest logit
    inds = torch.argsort(dist_matrix, dim=1, descending=True)
    inds = inds.to(device)

    image_to_text_recall = []

    for k in k_vals:
        # Extract top k indices only
        topk = inds[:, :k]

        correct = torch.zeros((num_im,), dtype=torch.bool).to(device)

        #  For each image, check whether one of the 5 relevant captions was retrieved
        # Check if image matches its ith caption (for i=0..4)
        for i in range(captions_per_image):
            contains_index = torch.eq(topk, image_to_text_map[:, i].unsqueeze(-1)).any(dim=1)
            correct = torch.logical_or(correct, contains_index)

        num_correct = correct.sum().item()
        image_to_text_recall.append(num_correct / num_im)#

    print("Done.")
    return text_to_image_recall, image_to_text_recall

def get_preprocess(n_px):
    return Compose([
        Resize(n_px, interpolation=BICUBIC),
        CenterCrop(n_px),
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
    ])
    
### REMOTECLIP ###
def load_remoteCLIP(model_name:str, device:str):
    model_name = model_name.split("_")[1]
    model, _, preprocess = open_clip.create_model_and_transforms(model_name)
    tokenizer = open_clip.get_tokenizer(model_name)
    
    ckpt = torch.load(f"/media/data_fast/Riccardo/RemoTextVision_benchmark/remoteCLIP/models--chendelong--RemoteCLIP/snapshots/bf1d8a3ccf2ddbf7c875705e46373bfe542bce38/RemoteCLIP-{model_name}.pt", map_location="cpu")
    model.load_state_dict(ckpt)
    model.to(device)
    
    return model, preprocess, tokenizer

### GEORSCLIP ###
def _convert_to_rgb(image):
    return image.convert('RGB')

def get_preprocess(image_resolution=224, subset_name="clip", aug=None):

    if subset_name == "clip":
        normalize = Normalize(
            mean=[0.48145466, 0.4578275, 0.40821073], std=[0.26862954, 0.26130258, 0.27577711]
        )
    elif subset_name == "imagenet":
        normalize = Normalize(
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        )

    elif subset_name == "rs5m":
        normalize = Normalize(
            mean=[0.406, 0.423, 0.390], std=[0.188, 0.175, 0.185]
        )

    elif subset_name == "pub11":
        normalize = Normalize(
            mean=[0.445, 0.469, 0.441], std=[0.208, 0.193, 0.213]
        )

    elif subset_name == "rs3":
        normalize = Normalize(
            mean=[0.350, 0.356, 0.316], std=[0.158, 0.147, 0.143]
        )

    elif subset_name == "geometa":
        normalize = Normalize(
            mean=[0.320, 0.322, 0.285], std=[0.179, 0.168, 0.166]
        )

    preprocess_val = Compose([
        Resize(
            size=image_resolution,
            interpolation=InterpolationMode.BICUBIC,
        ),
        CenterCrop(image_resolution),
        _convert_to_rgb,
        ToTensor(),
        normalize,
    ])
    return preprocess_val

def load_geoRSCLIP(model_name:str, device:str):
    model_name = model_name.split("_")[1]
    model, _, __ = open_clip.create_model_and_transforms(model_name)
    preprocess = get_preprocess(image_resolution=336)
    tokenizer = open_clip.get_tokenizer(model_name)
    
    ckpt = torch.load(f"/media/data_fast/Riccardo/RemoTextVision_benchmark/geoRSCLIP/models--Zilun--GeoRSCLIP/snapshots/0b7b13838d11b8ab43ca72706fd03d5177e3ffa9/ckpt/RS5M_{model_name}.pt", map_location="cpu")
    model.load_state_dict(ckpt)
    model.to(device)
    
    return model, preprocess, tokenizer


def load_clipRSICDv2(model_name:str, device:str):
    model_name = model_name.split("_")[1]
    model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name, do_rescale=False)
    tokenizer = None
    
    model.to(device)
    
    return model, processor, tokenizer

def encode_text_CLIPrsicdv2(model:CLIPModel, texts:List[str], device:str):
    '''
    This function takes a list of texts and returns their embeddings using CLIPrsicdv2
    '''
    textprocessor = CLIPTokenizer.from_pretrained("flax-community/clip-rsicd-v2")
    text_inputs = textprocessor(texts, return_tensors="pt", padding=True)
    text_embeddings = model.get_text_features(input_ids=text_inputs["input_ids"].to(device), attention_mask=text_inputs["attention_mask"].to(device))
    return text_embeddings

def encode_image_CLIPrsicdv2(model:CLIPModel, images:List[PIL.Image.Image], device:str):
    '''
    This function takes a list of images and returns their embeddings using CLIPrsicdv2
    '''
    imageprocessor = CLIPImageProcessor.from_pretrained("flax-community/clip-rsicd-v2")
    image_inputs = imageprocessor(images, return_tensors="pt")
    image_embeddings = model.get_image_features(pixel_values=image_inputs["pixel_values"].to(device))
    return image_embeddings


if __name__=="__main__":
    model = CLIPModel.from_pretrained("flax-community/clip-rsicd-v2")
    texts = ["a remote sensing image of a forest", "a remote sensing image of a city", "a remote sensing image of a river"]
    text_embs = encode_text_CLIPrsicdv2(model, texts, "cpu")
    print(text_embs.shape)