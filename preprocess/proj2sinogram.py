import numpy as np
import os
import argparse
import yaml
from tqdm import tqdm, trange


# Only do simple average
def air_average(air_correction):
    input_dir = air_correction['input_dir']
    output_dir = air_correction['output_dir']
    out_filename = air_correction['filename']
    w = air_correction['air_image_width']
    h = air_correction['air_image_height']

    filename_list = sorted(os.listdir(input_dir))  # all files under the directory
    temp = np.zeros(w * h, dtype=np.float32)

    for filename in tqdm(range(len(filename_list))):
        absolute_path = os.path.join(input_dir, filename_list[filename])
        with open(absolute_path, 'rb') as fp:  # once read one file and close
            temp += np.frombuffer(fp.read(), dtype=np.int16)  # 16 signed int

    air_average = temp / len(filename_list)
    with open(os.path.join(output_dir, out_filename), 'wb') as fp:
        fp.write(air_average.tobytes())


def proj2sinogram(projection_image, air_correction):
    # normal parameter
    input_dir = projection_image['input_dir']
    output_dir = projection_image['output_dir']
    out_filename = projection_image['filename']
    w = projection_image['projection_width']
    h = projection_image['projection_height']
    view = projection_image['view']
    image_count_per_slice = projection_image['image_count_per_slice']
    air_average_proportion_adjust = 1  # in case of no air correction
    air_average = 1  # in case of no air correction

    # use air correction or not
    use_air_correction = air_correction['use_air_correction']
    if use_air_correction:
        air_average_dir = air_correction['output_dir']
        air_average_filename = air_correction['filename']
        air_average_absolute_path = os.path.join(air_average_dir, air_average_filename)

        with open(air_average_absolute_path, 'rb') as fp:
            air_average = np.frombuffer(fp.read(), dtype=np.float32)  # 32 float
            print('- Air average image detected!')
        air_average_proportion_adjust = projection_image['air_average_proportion_adjust']

    # convert projection to sinogram
    filename_list = sorted(os.listdir(input_dir))  # all files under the directory
    postlog_img = np.zeros((h, view, w), dtype=np.float32)  # y, V, x format to save easily

    for i in trange(view):
        absolute_path = os.path.join(input_dir, filename_list[i])

        with open(absolute_path, 'rb') as fp:  # once read one file and close
            projection = np.frombuffer(fp.read(), dtype=np.int16)  # 16 signed int

        temp = np.log(air_average * air_average_proportion_adjust) - np.log(np.array(projection, dtype=np.float32))
        postlog_img[:, i, :] = temp.reshape((h, w))

    # slice the sinogram series to smaller pieces for quick reconstruction
    # each sinogram series do a simple average
    print('- Wait for slice combine...')
    step = image_count_per_slice
    slice_count = h // image_count_per_slice  # postlog_img.shape = (h, view, w)
    postlog_img_combine = np.zeros((slice_count, view, w), dtype=np.float32)
    for i in trange(slice_count):
        sub_postlog_img = postlog_img[i * step:] if (i + 1) * step > h \
                                                    else postlog_img[i * step:(i + 1) * step]
        
        postlog_img_combine[i, :, :] = sum(sub_postlog_img) / len(sub_postlog_img)

    print('- Wait for save...')
    with open(os.path.join(output_dir, out_filename), 'wb') as fp:
        fp.write(postlog_img_combine.tobytes())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(  # config file path
        '-d', '--dir', nargs='+', help='config_helper.yml path')
    args = parser.parse_args()

    config_file_path = args.dir[0]
    with open(config_file_path, 'r') as f:
        config_file = f.read()
    config_file_dict = yaml.load(config_file, Loader=yaml.FullLoader)

    air_correction = config_file_dict['AirCorrection']
    projection_image = config_file_dict['ProjectedImage']

    # Do air average
    if air_correction['use_air_correction']:
        print('Begin air image average...')
        air_average(air_correction)
        print('Done!')

    # Do projection to postlog sinogram
    print('Begin projection to postlog sinogram...')
    proj2sinogram(projection_image, air_correction)
    print('All Done!')