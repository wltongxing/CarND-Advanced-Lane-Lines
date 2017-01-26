import os
import pickle
import cv2
import numpy as np


class CameraCalibrator:
    def __init__(self, calibration_images, no_corners_x_dir, no_corners_y_dir):
        """

        :param calibration_images:
        :param no_corners_x_dir:
        :param no_corners_y_dir:
        """
        self.calibration_images = calibration_images
        self.no_corners_x_dir = no_corners_x_dir
        self.no_corners_y_dir = no_corners_y_dir
        self.object_points = []
        self.image_points = []

        self.calibrated_data_path = '../camera_cal/calibrated_data.p'

        self.mtx = None
        self.dict = None

    def calibrate(self):
        """

        :return:
        """
        object_point = np.zeros((self.no_corners_x_dir * self.no_corners_y_dir, 3), np.float32)
        object_point[:, :2] = np.mgrid[0:self.no_corners_x_dir, 0:self.no_corners_y_dir].T.reshape(-1, 2)

        for idx, file_name in enumerate(self.calibration_images):
            image = cv2.imread(file_name)
            gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            ret, corners = cv2.findChessboardCorners(gray_image,
                                                     (self.no_corners_x_dir, self.no_corners_y_dir),
                                                     None)
            if ret:
                self.object_points.append(object_point)
                self.image_points.append(corners)

        image_size = (image.shape[1], image.shape[0])
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.object_points,
                                                           self.image_points, image_size, None, None)
        calibrated_data = {'mtx': mtx, 'dist': dist}

        with open(self.calibrated_data_path, 'wb') as f:
            pickle.dump(calibrated_data, file=f)

    def undistort(self, image):

        if not os.path.exists(self.calibrated_data_path):
            raise Exception('xxx')

        with open(self.calibrated_data_path, 'rb') as f:
            calibrated_data = pickle.load(file=f)

        image = cv2.imread(image)
        return cv2.undistort(image, calibrated_data['mtx'], calibrated_data['dist'],
                             None, calibrated_data['mtx'])


if __name__ == '__main__':
    import glob
    import matplotlib.pyplot as plt

    images = glob.glob('../camera_cal/calibration*.jpg')

    calibrator = CameraCalibrator(images, 9, 6);
    #calibrator.calibrate()
    dest = calibrator.undistort('../camera_cal/calibration1.jpg')
    f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    img = cv2.imread('../camera_cal/calibration1.jpg')
    ax1.imshow(img)
    ax1.set_title('Original Image', fontsize=30)
    ax2.imshow(dest)
    ax2.set_title('Undistorted Image', fontsize=30)
    plt.show()