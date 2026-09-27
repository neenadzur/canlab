"""Axial thumbnails for neuromarkers.io tiles, replicating Neuroimaging_Pattern_Masks/site/scripts/build.py previews."""
import json,sys,gzip,tempfile,shutil
from pathlib import Path
import numpy as np, nibabel as nib
from scipy.ndimage import map_coordinates
from PIL import Image
# Usage: python scripts/render_neuromarker_thumbs.py <Neuroimaging_Pattern_Masks checkout> (needs nibabel, scipy, pillow)
ROOT=Path(sys.argv[1]); OUT=Path(__file__).resolve().parents[1]/'site/assets/img/neuromarkers'
def load(src):
    if src.name.endswith('.img.gz'):
        with tempfile.TemporaryDirectory() as t:
            loc=Path(t)/src.name[:-3]; loc.write_bytes(gzip.decompress(src.read_bytes()))
            hdr=src.with_suffix('').with_suffix('.hdr')
            if hdr.exists(): shutil.copyfile(hdr,loc.with_suffix('.hdr'))
            else: loc.with_suffix('.hdr').write_bytes(gzip.decompress(Path(str(hdr)+'.gz').read_bytes()))
            i=nib.load(loc); return nib.Nifti1Image(i.get_fdata(),i.affine)
    return nib.load(src)
sh=ROOT/'site/data/shared'
bm=nib.load(sh/'preview-brainmask.nii.gz'); brain=bm.get_fdata(dtype=np.float32)
an=nib.load(sh/'underlay.nii.gz'); anat=an.get_fdata(dtype=np.float32)
for s in json.load(open(ROOT/'site/data/catalog.json'))['studies']:
    src=ROOT/s['maps'][0]['source']
    try: img=load(src)
    except Exception as e: print('FAIL',s['id'],e); continue
    d=img.get_fdata(dtype=np.float32)
    if d.ndim==4: d=d[...,0]
    ras=nib.as_closest_canonical(nib.Nifti1Image(d,img.affine)); v=ras.get_fdata(dtype=np.float32)
    mc=nib.affines.apply_affine(np.linalg.inv(bm.affine)@ras.affine,np.indices(v.shape).reshape(3,-1).T)
    inside=map_coordinates(brain,mc.T,order=0,mode='constant',cval=0).reshape(v.shape)>0
    z=int(np.argmax(np.sum(np.abs(np.nan_to_num(v))*inside,axis=(0,1))))
    g=np.indices(v.shape[:2]); ijk=np.stack([g[0].ravel(),g[1].ravel(),np.full(g[0].size,z)],1)
    co=nib.affines.apply_affine(np.linalg.inv(an.affine)@ras.affine,ijk)
    bg=map_coordinates(anat,co.T,order=1,mode='constant').reshape(v.shape[:2])
    bg=np.clip(bg/(np.percentile(anat[anat>0],99) or 1),0,1)
    rgb=np.repeat((bg*165)[...,None],3,axis=2); sl=np.nan_to_num(v[:,:,z])
    for sign,stops,cols in [(1,[0,64,192,255],[[0,0,4],[120,28,109],[237,105,37],[240,249,33]]),(-1,[0,128,255],[[0,0,255],[0,128,196],[0,255,128]])]:
        vals=sign*v[np.isfinite(v)&(sign*v>0)]
        if not vals.size: continue
        cut=np.quantile(vals,0.65); mx=vals.max()
        act=inside[:,:,z]&(sign*sl>0)&(sign*sl>=cut)
        it=np.clip(np.abs(sl[act])/(mx or 1)*255,0,255)
        rgb[act]=np.stack([np.interp(it,stops,np.array(cols)[:,c]) for c in range(3)],-1)
    im=Image.fromarray(np.rot90(rgb.astype(np.uint8)))
    im=im.resize((im.width*4,im.height*4),Image.NEAREST)
    im.thumbnail((360,260),Image.LANCZOS)
    canvas=Image.new('RGB',(360,260),(0,0,0)); canvas.paste(im,((360-im.width)//2,(260-im.height)//2))
    canvas.save(OUT/f"{s['id']}.jpg",quality=86); print('ok',s['id'],z)
