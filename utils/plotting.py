import matplotlib.pyplot as plt

def save_streamlit_style_figure(fig, filename="plot_output.png", dpi=300, dark_mode=False):
    fig.set_size_inches(10, 6)
    fig.tight_layout()
    bg_color = "#0e1117" if dark_mode else "#ffffff"
    fg_color = "#ffffff" if dark_mode else "#000000"

    fig.patch.set_facecolor(bg_color)
    for ax in fig.get_axes():
        ax.set_facecolor(bg_color)
        ax.tick_params(colors=fg_color)
        ax.title.set_color(fg_color)
        ax.xaxis.label.set_color(fg_color)
        ax.yaxis.label.set_color(fg_color)

    fig.savefig(filename, dpi=dpi, facecolor=fig.get_facecolor())
    print(f"Saved figure to {filename}")