# Example Package

This is a simple example package. You can use
[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.


# Build Command
```bash
# if required 
pip install pipreqs
pipreqs /path/to/your/project
# requirements.txt pyproject.ml에 복사

```
```bash
python -m build
python -m twine upload --repository pypi dist/{package_name}-asdf.whl
```