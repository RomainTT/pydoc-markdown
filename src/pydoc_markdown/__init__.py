# -*- coding: utf8 -*-
# Copyright (c) 2019 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
Pydoc-markdown is an extensible framework for generating API documentation,
with a focus on Python source code and the Markdown output format.
"""


from nr.databind.core import Field, ObjectMapper, Struct, UnionType
from nr.databind.json import JsonModule
from pydoc_markdown.interfaces import Loader, Processor, Renderer
from pydoc_markdown.reflection import ModuleGraph
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
import logging
import yaml

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '3.0.0'

mapper = ObjectMapper(JsonModule())
logger = logging.getLogger(__name__)


class PydocMarkdown(Struct):
  loaders = Field([Loader], default=lambda: [PythonLoader()])
  processors = Field([Processor], default=lambda: [SmartProcessor(), FilterProcessor()])
  renderer = Field(Renderer, default=lambda: MarkdownRenderer())

  def __init__(self, *args, **kwargs):
    super(PydocMarkdown, self).__init__(*args, **kwargs)
    self.graph = ModuleGraph()

  def load_config(self, data):
    """ Loads a YAML configuration from *data*.

    Args:
      data (str, dict): If a string is specified, it is treated as the path
        to a YAML file.
    Return: self
    """

    filename = None
    if isinstance(data, str):
      filename = data
      logger.info('Loading configuration file "%s".', filename)
      with open(data) as fp:
        data = yaml.safe_load(fp)

    result = mapper.deserialize(data, type(self), filename=filename)
    vars(self).update(vars(result))
    return result

  def load_modules(self):
    for loader in self.loaders:
      loader.load(self.graph)

  def process(self):
    for processor in self.processors:
      processor.process(self.graph)

  def render(self):
    self.renderer.process(self.graph)
    self.renderer.render(self.graph)