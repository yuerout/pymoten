from moten import readers, colorspace
from importlib import reload
reload(readers)

##############################
# Video example
##############################

# single image
##############################
video_buffer = readers.video_buffer('avsnr150s24fps_sd.mp4')
image_rgb = video_buffer.__next__() # load a single image
vdim, hdim, cdim = image_rgb.shape
aspect_ratio = hdim/vdim

# single images
image_luminance = readers.imagearray2luminance(image_rgb, size=None)
image_luminance_resized = readers.imagearray2luminance(image_rgb, size=(96, int(96*aspect_ratio)))

# process is reversible
resized_image = readers.resize_image(image_rgb, size=(96, int(96*aspect_ratio)))
resized_image_luminance = readers.imagearray2luminance(resized_image, size=None)
assert np.allclose(image_luminance_resized[0], resized_image_luminance[0])

# NB: skimage comparison.
import skimage.color
skimage_cielab = skimage.color.rgb2lab(image_rgb)
skimage_luminance = skimage_cielab[...,0]
# skimage is not the same...
assert np.allclose(skimage_luminance, image_luminance[0]) is False
# ...But it is highly correlated.
corr = np.corrcoef(skimage_luminance.ravel(), image_luminance[0].ravel())[0,1]
assert corr > 0.999
# Neither the observer nor the illuminant options account for this difference.
# TODO: Figure out the exact reason for this difference.


# multiple images
##############################

# load only 100 images
video_buffer = readers.video_buffer('avsnr150s24fps_sd.mp4', nimages=100)

images_rgb = np.asarray([image for image in video_buffer])
nimages, vdim, hdim, cdim = images_rgb.shape
aspect_ratio = hdim/vdim

images_luminance = readers.imagearray2luminance(images_rgb,
                                               size=None)
images_luminance_resized = readers.imagearray2luminance(images_rgb,
                                                        size=(96, int(96*aspect_ratio)))

assert np.allclose(images_luminance_resized[0], image_luminance_resized[0])

# test video2luminance generator
nimages = 256
video_buffer = readers.video_buffer('avsnr150s24fps_sd.mp4', nimages=nimages)
# load and downsample 1000 images
aspect_ratio = 16/9.0
small_size = (96, int(96*aspect_ratio))

luminance_images = np.asarray([readers.imagearray2luminance(image, size=small_size).squeeze() \
                               for image in video_buffer])

lum = readers.video2luminance('avsnr150s24fps_sd.mp4', size=small_size, nimages=nimages)
assert np.allclose(luminance_images, lum)


##############################
# Example with PNG images
##############################
from glob import glob
image_files = sorted(glob('*.png'))
files_luminance = readers.load_image_luminance(image_files)

files_luminance_resized = readers.load_image_luminance(image_files,
                                                       vdim=96, hdim=int(96*aspect_ratio))

assert np.allclose(files_luminance, images_luminance)
assert np.allclose(files_luminance_resized, images_luminance_resized)
