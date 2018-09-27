from pip._internal import index
from pip._internal.commands.freeze import FreezeCommand
from pip._internal.commands.show import ShowCommand, search_packages_info
from pip._internal.cache import WheelCache
from pip._internal.compat import stdlib_pkgs
from pip._internal.operations.freeze import freeze

DEV_PKGS = {'pip', 'setuptools', 'distribute', 'wheel'}

options, args = FreezeCommand().parse_args([])

format_control = index.FormatControl(set(), set())
wheel_cache = WheelCache(options.cache_dir, format_control)
skip = set(stdlib_pkgs)
if not options.freeze_all:
    skip.update(DEV_PKGS)

freeze_kwargs = dict(
    requirement=options.requirements,
    find_links=options.find_links,
    local_only=options.local,
    user_only=options.user,
    skip_regex=options.skip_requirements_regex,
    isolated=options.isolated_mode,
    wheel_cache=wheel_cache,
    skip=skip,
    exclude_editable=options.exclude_editable,
)

# build a list of packages that are currently installed
packages = {}
for item in list(freeze(**freeze_kwargs)):
    k, v = item.split('==')
    packages[k] = v

# Get the package info for all installed packages
packages_info = search_packages_info(packages.keys())

# Build a set of dependencies
for package in list(packages.keys()):
    dependencies = list(search_packages_info([package]))[0]['requires']
    for dependency in dependencies:
        # don't remove the dependency if the package is prefixed with the dependency indicating
        # it's an extension.
        if dependency.lower() != package.lower()[0:len(dependency)]:
            try:
                del packages[dependency]
            except KeyError:
                pass

lines = []
for k, v in packages.items():
    lines.append('{}=={}'.format(k, v))

print('\n'.join(sorted(lines)))
