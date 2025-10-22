import os
import glob
import imageio.v2 as imageio
import matplotlib.pyplot as plt
import osh5io
import osh5vis

class PlasmaGifMaker:
    def __init__(self, data_dir, pattern, output_name="plasma_evolution.gif", sort_key=None):
        """
        Parameters
        ----------
        data_dir : str
            Directory containing OSIRIS HDF5 output files.
        output_name : str
            Name of the output GIF file.
        sort_key : callable, optional
            Function for sorting files, e.g. by timestep number.
        """
        self.data_dir = data_dir
        self.output_name = output_name
        self.sort_key = sort_key
        self.pattern = pattern

    def _get_files(self):
        files = glob.glob(os.path.join(self.data_dir, self.pattern))
        if not files:
            raise FileNotFoundError(f"No files found in {self.data_dir} matching {self.pattern}")
        if self.sort_key:
            files.sort(key=self.sort_key)
        else:
            files.sort()
        return files

    def create_gif(self, fps=5, figsize=(6,5), save_frames=False):
        """
        Generates a GIF from OSIRIS data files.

        Parameters
        ----------
        pattern : str
            File name pattern for diagnostic files (e.g. 'charge*.h5', 'B3*.h5', etc.)
        fps : int
            Frames per second in the resulting GIF.
        cmap : str
            Matplotlib colormap name.
        figsize : tuple
            Figure size for plots.
        save_frames : bool
            If True, saves individual PNG frames.
        """
        files = self._get_files()
        images = []

        temp_dir = os.path.join(self.data_dir, "frames")
        if save_frames:
            os.makedirs(temp_dir, exist_ok=True)

        for i, f in enumerate(files):
            data = osh5io.read_h5(f)
            fig, ax = plt.subplots(figsize=figsize)
            osh5vis.osplot(data, ax=ax)
            ax.set_title(f"time step {i}")

            # Save temporary frame
            tmp_path = os.path.join(temp_dir, f"frame_{i:04d}.png") if save_frames else f"/tmp/frame_{i:04d}.png"
            plt.savefig(tmp_path, bbox_inches=None, dpi=120)
            plt.close(fig)

            images.append(imageio.imread(tmp_path))

        # Save GIF
        gif_path = os.path.join(self.data_dir, self.output_name)
        imageio.mimsave(gif_path, images, fps=fps)
        print(f"✅ GIF saved at {gif_path}")

        if not save_frames:
            # Clean up /tmp frames automatically
            for tmp in [f"/tmp/frame_{i:04d}.png" for i in range(len(images))]:
                if os.path.exists(tmp):
                    os.remove(tmp)
