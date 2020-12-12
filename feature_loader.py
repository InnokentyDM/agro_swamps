import geopandas
import matplotlib.pyplot as plt

DATASET_PATH = 'static/Marshes.geojson'


def plot_initial_data():
    df = geopandas.read_file(DATASET_PATH)
    print(df.shape)
    print(df.head())

    df['centroid_column'] = df.centroid
    df = df.set_geometry('centroid_column')
    df.plot()
    plt.show()


if __name__ == '__main__':
    plot_initial_data()
