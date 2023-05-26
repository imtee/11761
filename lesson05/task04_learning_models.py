import cv2
import numpy as np
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from utils import sample_filepath


def train_and_test_model():
    img = cv2.imread(sample_filepath('Retinal_DRIVE21_original.tif'), cv2.IMREAD_GRAYSCALE)
    mask = cv2.imread(sample_filepath('Retinal_DRIVE21_gt.tif'), cv2.IMREAD_GRAYSCALE)

    # Get features
    X = features_gabor_filter_bank(img)
    # or X = features_eigenvalues_hessian(img)
    # or X = np.concatenate([features_gabor_filter_bank(img), features_eigenvalues_hessian(img)], axis=1)

    # Get labels
    num_pixels = img.shape[0] * img.shape[1]
    y = mask.flatten()/255

    # Create model
    model = LogisticRegression()
    # or model = RandomForestClassifier()

    # Train model
    random_selection_positives = np.random.choice(np.where(y == 1)[0], 5000, replace=False)
    random_selection_negatives = np.random.choice(np.where(y == 0)[0], 5000, replace=False)
    random_selection = np.concatenate([random_selection_positives, random_selection_negatives])
    X_train = X[random_selection, :]
    y_train = y[random_selection]
    # YOUR CODE HERE:
    #   Use `model.fit(X, y)` to train the model.
    #   ...
    model.fit(X_train, y_train)

    # Make predictions
    # YOUR CODE HERE:
    #   Use `model.predict(X)` to train the model.
    #   ...
    predictions = np.zeros_like(y)  # You may delete this line.
    predictions = model.predict(X).reshape(img.shape)

    # Plot
    #   Arrange tensor for better visualizations
    img_with_gt = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img_with_gt[mask == 255] = [0, 0, 255]
    img_with_pred = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img_with_pred[predictions == 1] = [0, 255, 0]
    #   Create figure
    _, axs = plt.subplots(2, 2)
    axs[0, 0].imshow(img, cmap='gray')
    axs[0, 1].set_axis_off()
    axs[1, 0].imshow(img_with_gt)
    axs[1, 1].imshow(img_with_pred)
    plt.show()


def features_gabor_filter_bank(img):
    """Computes features based on Gabor filters."""
    # This function is already provided.
    kernels = [
        cv2.getGaborKernel(ksize=(15, 15), sigma=sigma, theta=theta, lambd=lambd, gamma=gamma, psi=0)
        for sigma in [3, 5, 7]
        for theta in [np.pi, np.pi / 2, 0]
        for lambd in [1.5, 2]
        for gamma in [1, 1.5]
    ]
    filtered_images = [cv2.filter2D(img, cv2.CV_64F, kernel) for kernel in kernels]

    # Create features
    X = np.stack([f.flatten() for f in filtered_images], axis=-1)
    return X


def features_eigenvalues_hessian(img):
    """Computes features based on the eigenvalues of the Hessian matrix."""
    # YOUR CODE HERE
    #   ...
    hessian_dxdx = cv2.Sobel(img, cv2.CV_32F, 2, 0, ksize=3)
    hessian_dxdy = cv2.Sobel(img, cv2.CV_32F, 1, 1, ksize=3)
    hessian_dydx = hessian_dxdy
    hessian_dydy = cv2.Sobel(img, cv2.CV_32F, 0, 2, ksize=3)

    hessian_det = hessian_dxdx * hessian_dydy - hessian_dxdy * hessian_dydx
    hessian_trace = hessian_dxdx + hessian_dydy
    # Solve `x^2 - trace * x + det = 0`
    hessian_eigenvalue_1 = 0.5 * (hessian_trace + np.sqrt(hessian_trace**2 - 4 * hessian_det))
    hessian_eigenvalue_2 = 0.5 * (hessian_trace - np.sqrt(hessian_trace**2 - 4 * hessian_det))

    X = np.stack([hessian_det.flatten(), hessian_trace.flatten(), hessian_eigenvalue_1.flatten(), hessian_eigenvalue_2.flatten()], axis=-1)
    return X


if __name__ == '__main__':
    train_and_test_model()