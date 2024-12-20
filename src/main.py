import RootWindow as rw


def main():
    root = rw.RootWindow()
    root.PulsingChild().DigitizerChild().PlottingChild().RunFrame().mainloop()

if __name__ == "__main__":
    main()
