from setuptools import Extension, setup
from Cython.Build import cythonize

extensions = [
    Extension(
        "chronosmatch.engine_cython",
        ["chronosmatch/engine_cython.pyx"],
    )
]

setup(
    name="chronosmatch",
    ext_modules=cythonize(
        extensions,
        compiler_directives={"language_level": "3"},
    ),
)
