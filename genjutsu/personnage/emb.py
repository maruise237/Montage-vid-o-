import os, torch
M=os.environ.get('GENJUTSU_MODELS', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')) + '/vace13'
prompt = ('A young African man, slim athletic build, very short clean fade haircut, wearing a black graphic t-shirt '
          'with blue and white abstract design and small logo, long brown chino trousers covering the legs down to the ankles, black crossbody bag, black and gray sneakers, '
          'playing football on a stadium pitch at night, dynamic motion, realistic, sharp details')
neg = 'shorts, bare legs, bare knees, robe, gown, hat, cap, sunglasses, blurry, deformed, extra limbs, low quality, cartoon, text, watermark'
emb = M + '/../prompt_embeds.pt'
if not os.path.exists(emb):
    from transformers import UMT5EncoderModel, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(M, subfolder='tokenizer')
    te = UMT5EncoderModel.from_pretrained(M, subfolder='text_encoder', torch_dtype=torch.bfloat16, low_cpu_mem_usage=True)
    def enc(t):
        ids = tok([t], padding='max_length', max_length=512, truncation=True, return_tensors='pt')
        with torch.inference_mode():
            h = te(ids.input_ids, ids.attention_mask).last_hidden_state.clone()
            L = int(ids.attention_mask.sum()); h[:, L:] = 0
        return h
    torch.save({'p': enc(prompt), 'n': enc(neg)}, emb)
    del te
    print('ok')
