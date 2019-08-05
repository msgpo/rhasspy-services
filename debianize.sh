#!/usr/bin/env bash
if [[ -z "$3" ]]; then
    echo "Usage: debianize.sh CATEGORY NAME ARCH [VERSION]"
    exit 1
fi

category="$1"
name="$2"
arch="$3"
version="$4"

if [[ -z "${verson}" ]]; then
    version="1.0"
fi

package_name="rhasspy-${name}_${version}_${arch}"
package_dir="debian/${category}/${package_name}"
output_dir="${package_dir}/usr/lib/rhasspy/${name}"

# Copy PyInstaller-generated files
rsync -av --delete \
      "dist/${name}/" \
      "${output_dir}"

# Remove all symbols (Liantian warning)
strip --strip-all "${output_dir}"/*.so*

# Remove executable bit from shared libs (Lintian warning)
chmod -x "${output_dir}"/*.so*

# Actually build the package
cd "debian/${category}" && fakeroot dpkg --build "${package_name}"
