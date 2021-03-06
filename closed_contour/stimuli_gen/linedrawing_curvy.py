# This code generates images of size 256 x 256 px that contains either an open or closed contour.
# This contour consists of curved lines that were generated by radial frequency distortions.
# author: Christina Funke

import numpy as np
import os
from PIL import Image
from pathlib import Path


def radial_frequency_linewidth(
    size_im=288,
    radius_circle=80,
    shift_x=0,
    shift_y=0,
    line_width=6,
    frequency=7,
    amplitude=18,
    phase=0,
    frequency2=0,
    amplitude2=0,
    phase2=0,
    gapsize=0,
    gapphase=0,
    dash_numgaps=0,
    dash_phase=0,
):
    """
    Makes a (closed/ open/ dashed) contour defined by 2 sinusoidal components with equal linewidth
    
    Args:
        size_im (int): the size of the output image
        radius_circle (float): size of the modulated circle
        shift_x (float): shift the contour in x direction (relative to center, positive means shift right)
        shift_y(float): shift the contour in y direction (relative to center, positive means shift down)
        line_width (float): thickness of the line
        frequency (int): modulation frequency
        amplitude (float): modulation amplitude
        phase (float): modulation phase
        frequency2 (int): second modulation frequency
        amplitude2 (float): second modulation amplitude
        phase2 (float): second modulation phase
        
        gapsize (float): size of the gap of the open contour (0 for closed contour) 
        gapphase (float): phase of the gap of the open contour 
        
        dash_numgaps (int): number of gaps for dashed contour
        dash_phase (float): phase of the dashed line segments
        
    Returns:
        image (int array): the image containing a closed contour

    Example:
        res = radial_frequency_linewidth()
    """

    start, end = (
        0 + gapphase,
        2 * np.pi + gapphase - gapsize,
    )  # make open contour if gapsize is larger than 0
    phi = np.linspace(start, end, 500)

    # make dashed contour
    if dash_numgaps != 0:
        dash_mask = np.sin(dash_numgaps * phi + dash_phase) > 0
        phi = phi[dash_mask]

    r = (
        amplitude * np.sin(frequency * (phi + phase))
        + amplitude2 * np.sin(frequency2 * (phi + phase2))
        + radius_circle
    )
    x = r * np.sin(phi) + shift_x
    y = r * np.cos(phi) + shift_y

    res = np.ones([size_im, size_im])
    for i in range(len(x)):
        xi = x[i] + size_im // 2
        yi = y[i] + size_im // 2

        # draw a circle with radius of half of the linewidth around each point xi, yi
        for xn in range(int(xi - 2 * line_width // 2), int(xi + 2 * line_width // 2)):
            for yn in range(
                int(yi - 2 * line_width // 2), int(yi + 2 * line_width // 2)
            ):
                if (xn - xi) ** 2 + (yn - yi) ** 2 < (line_width // 2) ** 2:
                    res[int(yn), int(xn)] = 0
    return res


def overlay_contours(im1, im2):
    """
    add two images: necessary for two contours in the image
    """
    return np.logical_and(im1, im2)


def save_image(im, contour, number, method, stim_folder):
    im = Image.fromarray(im * 255.0)
    im = im.resize((256, 256), Image.ANTIALIAS)
    im = im.convert("RGB")

    # save image
    number += 1
    filename = method + str(number)
    im.save(os.path.join(stim_folder, method, contour, filename + ".png"))
    return number


def make_full_dataset(top_dir, set_num, debug):
    """
    generate and save the full data set for a specified variation
    :param top_dir: where to save the images [string]
    :param set_num: number that specifies the variation [one of: 17, 18, 19, 20, 21, 22, 23]
    :param debug: generate only seven images [bool]
    """

    if debug:
        num_rep = 2  # 2800 # equals 5600 images
    else:
        num_rep = 2800  # equals to 5600 images

    np.random.seed(1)
    method = "test"

    stim_folder = top_dir + "set" + str(set_num) + "/linedrawing/"

    # make folder
    new_folder = os.path.join(stim_folder, method)
    print(new_folder)
    if not Path(new_folder).is_dir():
        print("make new folder")
        os.makedirs(new_folder)

    # make folders: open, closed
    new_folder = os.path.join(stim_folder, method, "open")
    if not Path(new_folder).is_dir():
        os.mkdir(new_folder)

    new_folder = os.path.join(stim_folder, method, "closed")
    if not Path(new_folder).is_dir():
        os.mkdir(new_folder)

    number = 0
    for rep in range(num_rep):
        # set parameters
        size_im = 1024
        radius_circle = np.random.rand() * 100 + 100
        shift_x, shift_y = 0, 0

        line_width = 10

        frequency = np.random.randint(1, 7)  # first frequency
        amplitude = np.random.rand() * 30 + 15
        phase = np.random.rand() * 2 * np.pi

        frequency2 = np.random.randint(1, 7)  # second frequency
        amplitude2 = np.random.rand() * 30 + 15
        phase2 = np.random.rand() * 2 * np.pi

        gapsize = np.pi / 3  # gap for open contour
        gapphase = np.random.rand() * 2 * np.pi
        dash_phase = np.random.rand() * 2 * np.pi
        dash_numgaps = 0

        if set_num == 18:  # dashed lines
            dash_numgaps = 20

        elif set_num == 19:  # dashed flanker
            shift_x, shift_y = (
                np.sign(np.random.randn()) * 200,
                np.sign(np.random.randn()) * 200,
            )
            shift_x_flanker, shift_y_flanker = -shift_x, -shift_y
            # make flanker
            resflanker = radial_frequency_linewidth(
                size_im=size_im,
                radius_circle=np.random.rand() * (200 - 100) + 100,
                shift_x=shift_x_flanker,
                shift_y=shift_y_flanker,
                line_width=line_width,
                frequency=np.random.randint(1, 7),
                amplitude=np.random.rand() * 30 + 15,
                phase=np.random.rand() * 2 * np.pi,
                frequency2=np.random.randint(1, 7),
                amplitude2=np.random.rand() * 30 + 15,
                phase2=np.random.rand() * 2 * np.pi,
                gapsize=0,
                gapphase=0,
                dash_numgaps=20,
                dash_phase=np.random.rand() * 2 * np.pi,
            )

        elif set_num == 20:  # diameter circle 50px
            radius_circle = 100

        elif set_num == 21:  # diameter circle 100px
            radius_circle = 200

        elif set_num == 22:  # diameter circle 150px
            radius_circle = 300

        elif set_num == 23:  # diameter circle 50px, add 1-4 flanker
            radius_circle = 100
            num_flanker = np.random.randint(1, 4)
            possible_shift = [
                [0, 0],
                [300, -300],
                [-300, 300],
                [300, 300],
                [-300, -300],
            ]
            np.random.shuffle(possible_shift)
            shift_x, shift_y = possible_shift[-1]

        # make closed contour image
        resclosed = radial_frequency_linewidth(
            size_im=size_im,
            radius_circle=radius_circle,
            shift_x=shift_x,
            shift_y=shift_y,
            line_width=line_width,
            frequency=frequency,
            amplitude=amplitude,
            phase=phase,
            frequency2=frequency2,
            amplitude2=amplitude2,
            phase2=phase2,
            gapsize=0,
            gapphase=0,
            dash_numgaps=dash_numgaps,
            dash_phase=dash_phase,
        )

        # make open contour image
        resopen = radial_frequency_linewidth(
            size_im=size_im,
            radius_circle=radius_circle,
            shift_x=shift_x,
            shift_y=shift_y,
            line_width=line_width,
            frequency=frequency,
            amplitude=amplitude,
            phase=phase,
            frequency2=frequency2,
            amplitude2=amplitude2,
            phase2=phase2,
            gapsize=gapsize,
            gapphase=gapphase,
            dash_numgaps=dash_numgaps,
            dash_phase=dash_phase,
        )

        if set_num == 19:
            resclosed = overlay_contours(resclosed, resflanker)
            resopen = overlay_contours(resopen, resflanker)

        if set_num == 23:
            for flanker in range(num_flanker):
                resflanker = radial_frequency_linewidth(
                    size_im=size_im,
                    radius_circle=radius_circle,
                    shift_x=possible_shift[flanker][0],
                    shift_y=possible_shift[flanker][1],
                    line_width=line_width,
                    frequency=np.random.randint(1, 7),
                    amplitude=np.random.rand() * 30 + 15,
                    phase=np.random.rand() * 2 * np.pi,
                    frequency2=np.random.randint(1, 7),
                    amplitude2=np.random.rand() * 30 + 15,
                    phase2=np.random.rand() * 2 * np.pi,
                    gapsize=gapsize,
                    gapphase=np.random.rand() * 2 * np.pi,
                    dash_numgaps=dash_numgaps,
                    dash_phase=dash_phase,
                )
                resclosed = overlay_contours(resclosed, resflanker)
                resopen = overlay_contours(resopen, resflanker)

        number = save_image(resclosed, "closed", number, method, stim_folder)
        number = save_image(resopen, "open", number, method, stim_folder)
