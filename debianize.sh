#!/usr/bin/env bash
set -e

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
mkdir -p "${output_dir}"

# Copy PyInstaller-generated files
rsync -av --delete \
      "dist/${name}/" \
      "${output_dir}"

# Remove all symbols (Liantian warning)
strip --strip-all "${output_dir}"/*.so* || true

# Remove executable bit from shared libs (Lintian warning)
chmod -x "${output_dir}"/*.so* || true

# Copy bin scripts
bin_dir="${category}/${package_name}/bin"
if [[ -d "${bin_dir}" ]]; then
    mkdir -p "${output_dir}/usr/bin"
    cp "${bin_dir}"/rhasspy-* "${output_dir}/usr/bin/"
fi

# Actually build the package
cd "debian/${category}" && fakeroot dpkg --build "${package_name}"
