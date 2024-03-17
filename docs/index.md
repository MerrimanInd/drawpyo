# Welcome to drawpyo

Drawpyo is a Python library for programmatically generating [Draw.io](https://www.drawio.com/) charts. It enables creating a diagram object, placing and styling objects, then writing the object to a file.

# History/Justification

I love Draw.io! Compared to expensive and heavy commercial options like Visio and Miro, Draw.io's free and lightweight app allows wider and more universal distribution of diagrams. Because the files are stored in plaintext they can be versioned alongside code in a repository as documentation. Draw.io also maintains back compatibility and any diagram created in the app since it was launched can still be opened. The XML-based file format makes these diagrams semi-portable, and could easily be ported to other applications if Draw.io ever disappeared. For these reason, I think it's one of the best options for documentation diagrams.

So wen I had a need to generate heirarchical tree diagrams of requirement structures I looked to Draw.io but I was surprised to find there wasn't even a single existing Python library for working with these files. I took the project home and spent a weekend building the initial functionality. I've been adding functionality, robustness, and documentation intermittently since.

# The Future of Drawpyo

I will continue to tinker away with this tool, creating new functionality as I need it or find it interesting. But it's unfortunately a rather low priority so if anyone wants to contribute I would be grateful for the help! Reach out to me at [xander@merriman.industries](mailto:xander@merriman.industries) if you want to contribute.