# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import functools
import inspect

from aiopyramid.config import CoroutineOrExecutorMapper


class WarehouseMapper(CoroutineOrExecutorMapper):

    def __call__(self, view):
        # If this is one of our views, then we want to enable passing the
        # request.matchdict into the view function as kwargs, we also want
        # to use asyncio coroutines to handle our own views.
        if view.__module__.startswith("warehouse."):
            # Wrap our view with our wrapper which will pull items out of the
            # matchdict and pass it into the given view.
            view = self._wrap_with_matchdict(view)

            # Wrap this as a coroutine so that it'll get called correctly from
            # asyncio.
            view = asyncio.coroutine(view)

        # Call into the aiopyramid CoroutineOrExecutorMapper which will call
        # this view as either a coroutine or as a sync view.
        return super().__call__(view)

    def _wrap_with_matchdict(self, view):
        @functools.wraps(view)
        def wrapper(context, request):
            kwargs = request.matchdict.copy()

            if inspect.isclass(view):
                inst = view(request)
                meth = getattr(inst, self.attr)
                return meth(**kwargs)
            else:
                return view(request, **kwargs)

        return wrapper
