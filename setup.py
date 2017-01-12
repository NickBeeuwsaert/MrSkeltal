from setuptools import setup

setup(
    name='MrSkeltal',
    version='0.0.0',
    description='Simple Project to test vertex skinning',
    author='Nick Beeuwsaert',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    packages=[
        'mr_skeltal'
    ],
    install_requires=[
        'PyOpenGL',
        'PyOpenGL-accelerate',
        'Pillow',
        'numpy'
    ],
    extras_require={
        'dev': [
            'pyflakes',
            'flake8-quotes'
        ],
        'test': [
            'pytest'
        ]
    }
)
