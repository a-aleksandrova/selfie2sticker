from processing import*
from test_rect import*
from test_paint import*
from minor_features import*
import cv2 as cv
import numpy as np

filename = 'ks.jpg'

img = getPngImg(filename)
img = setNormSize(img)

sf_img = nparray2surfase(img)
rectangle = get_rects(sf_img)

mask = np.zeros(img.shape[:2], np.uint8)
bgdModel = np.zeros((1, 65), np.float64)
fgdModel = np.zeros((1, 65), np.float64)
cv.grabCut(img, mask, rectangle, bgdModel, fgdModel, 5, cv.GC_INIT_WITH_RECT)

fg_mask = getMask(mask)
img_with_contour = showContour(img, fg_mask)


feedback = getFeedback(img_with_contour, 'Do you want to edit the borders?[y/n]')
manual_mode = None
while feedback == 'y':
    sf_img_with_contour = nparray2surfase(img_with_contour)
    print('orange -- for fg\nblue -- for bg\nalt -- change color\n+- -- change thickness')
    sf_markers = getMarker(sf_img_with_contour) #run paint
    bgr_markers = surface2nparray(sf_markers)
    markers = bgr_markers[:,:,2] #get red channel

    if manual_mode == None:
        mask[markers == 0] = 0
        mask[markers == 255] = 1
        mask, bgdModel, fgdModel = cv.grabCut(img, mask, None, bgdModel, fgdModel, 5, cv.GC_INIT_WITH_MASK)
        fg_mask = mask

    fg_mask = getMask(fg_mask, markers=markers, flag=manual_mode)
    img_with_contour = showContour(img, fg_mask)

    manual_mode = getFeedback(img_with_contour, 'Does the border still need to be changed?[y/n]')
    feedback = manual_mode


fg_img = remoweBg(img, fg_mask)

crop_feedback = getFeedback(fg_img, 'Crop the image?[y/n]')
if crop_feedback == 'y':
    fg_img, fg_mask = cropImgMask(fg_img, fg_mask)

fg_img = cv.copyMakeBorder(fg_img, 30, 30, 30, 30, cv.BORDER_CONSTANT)
fg_mask = cv.copyMakeBorder(fg_mask, 30, 30, 30, 30, cv.BORDER_CONSTANT)

norm_img = setNormSize(fg_img)
norm_mask = setNormSize(fg_mask)

result = showContour(norm_img, norm_mask, color=black, thikhess=3, flag='draw')

smooth_feedback = getFeedback(result, 'Smooth image?[y/n]')
if smooth_feedback == 'y':
    result = smoothing(result)


finish_feedback = getFeedback(result, 'Save the result?[y/n]')
if finish_feedback == 'y':
    print('Input name:')
    name = input()
    cv.imwrite('{}.png'.format(name), result)
    print('Result saved as {}.png'.format(name))

elif finish_feedback == 'n':
    print('Result not saved')


