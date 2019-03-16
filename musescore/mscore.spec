# Build packages:
#   mscore.x86_64 : Music Composition & Notation Software
#   mscore-doc.noarch : MuseScore documentation
#   mscore-fonts.noarch : MuseScore fonts

####################################################################################################

%global font_family_name %{name}
%global short_version 3.0

####################################################################################################

Name:          mscore
Summary:       Music Composition & Notation Software
Version:       %{short_version}.5
Release:       1%{?dist}
# rtf2html is LGPLv2+
# paper4.png paper5.png are LGPLv3
# the rest is GPLv2
# Soundfont is MIT
# Bravura and gootville are OFL
License:       GPLv2 and LGPLv2+ and LGPLv3 and CC-BY and MIT and OFL
Group:         Applications/Multimedia
URL:           http://musescore.org/en
Source0:       https://github.com/musescore/MuseScore/releases/download/v3.0.5/MuseScore-3.0.5.zip

####################################################################################################

# For mime types
Source1:       %{name}.xml
# Add metainfo file for font to show in gnome-software
Source2:       %{font_family_name}.metainfo.xml
# Use Fedora's default soundfont directory instead of the custom location
Patch0:        mscore-3.0.5-use-default-soundfont.patch
# We don't build the common files (font files, wallpapers, demo song, instrument
# list) into the binary executable to reduce its size. This is also useful to
# inform the users about the existence of different choices for common files.
# The font files need to be separated due to the font packaging guidelines.
Patch1:        mscore-3.0.5-separate-commonfiles.patch
# remove Version from desktop.in
Patch2:        mscore-2.0.3-fix-desktop-file.patch
# Use CXXFLAGS for precompiled header
Patch3:        musescore-2.0.1-fix-flags-for-precompiled-header.patch
# correct fonts-tabulature.xml location
Patch4:        MuseScore-2.0.1-fix-fonts_tabulature.patch
# Ensure CMake will use qmake-qt5
Patch5:        mscore-3.0.5-fix-qmake-path.patch

####################################################################################################

BuildRequires: alsa-lib-devel
BuildRequires: cmake
BuildRequires: desktop-file-utils
BuildRequires: gcc-c++
BuildRequires: jack-audio-connection-kit-devel
BuildRequires: pulseaudio-libs-devel
BuildRequires: libsndfile-devel
BuildRequires: portaudio-devel
BuildRequires: portmidi-devel
BuildRequires: libvorbis-devel
BuildRequires: qt5-qtbase-devel
# uses private api (somewhere)
BuildRequires: qt5-qtbase-private-devel
%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}
BuildRequires: qt5-qtdeclarative-devel
BuildRequires: qt5-qtscript-devel
BuildRequires: qt5-qttools-devel
BuildRequires: qt5-qttools-static
BuildRequires: qt5-qtsvg-devel
BuildRequires: qt5-qtxmlpatterns-devel
BuildRequires: qt5-qtwebengine-devel
BuildRequires: qt5-qtwebkit-devel
BuildRequires: qtsingleapplication-qt5-devel
BuildRequires: pkgconfig(freetype2) >= 2.5.2
BuildRequires: perl(Pod::Usage)
BuildRequires: doxygen

Requires:      %{name}-fonts = %{version}-%{release}
Requires:      soundfont2-default
# For scripting
Requires:      qt5-qtquickcontrols

# Doxygen documentation is huge and it is for musescore development only.
# Hence we don't build it for now. Otherwise it needs:
# BuildRequires: graphviz doxygen texlive-latex texlive-dvips

####################################################################################################

Provides:      musescore = %{version}-%{release}

####################################################################################################

%description
MuseScore is a free cross platform WYSIWYG music notation program. Some
highlights:

    * WYSIWYG, notes are entered on a "virtual note sheet"
    * Unlimited number of staves
    * Up to four voices per staff
    * Easy and fast note entry with mouse, keyboard or MIDI
    * Integrated sequencer and FluidSynth software synthesizer
    * Import and export of MusicXML and Standard MIDI Files (SMF)
    * Translated in 26 languages

####################################################################################################

%package doc
Summary:       MuseScore documentation
Group:         Documentation
License:       CC-BY
Requires:      %{name} = %{version}-%{release}
BuildArch:     noarch

%description doc
MuseScore is a free cross platform WYSIWYG music notation program.

This package contains the user manual of MuseScore in different languages.

####################################################################################################

%package fonts
Summary:       MuseScore fonts
Group:         User Interface/X
License:       GPL+ with exceptions and OFL
Requires:      fontpackages-filesystem
BuildArch:     noarch
BuildRequires: fontforge
BuildRequires: fontpackages-devel
BuildRequires: t1utils
BuildRequires: texlive
BuildRequires: tex-cm-lgc
BuildRequires: texlive-metapost-bin
BuildRequires: texlive-mf2pt1-bin
BuildRequires: lame-devel

%description fonts
MuseScore is a free cross platform WYSIWYG music notation program.

This package contains the musical notation fonts for use of MuseScore.

####################################################################################################

%prep
%setup -q -c MuseScore-%{short_version}

%patch0 -p1 -b .default.soundfont
%patch1 -p1 -b .separatecommon
%patch2 -p1 -b .fixdesktop
%patch3 -p1 -b .fixflags
%patch4 -p1

# porttime is part of portmidi in our distribution
sed -i 's|-lporttime||' mscore/CMakeLists.txt

# Remove the precompiled binary
rm thirdparty/rtf2html/rtf2html

# Remove bundled stuff
sed -i \
  -e "s|QtSolutions_SingleApplication-2.6|Qt5Solutions_SingleApplication-2.6|" \
  -e "/QTSINGLEAPPLICATION_INCLUDE_DIRS/s|)| PATHS %{_includedir}/qt5)|" \
  CMakeLists.txt
sed -i -e 's|#include "singleapp/src/QtSingleApplication"|#include <QtSingleApplication>|' mscore/musescore.h
rm -vrf thirdparty/singleapp
rm -vrf thirdparty/freetype

rm demos/All_Dudes.mscz demos/Triumph.mscz
sed -i -e 's|All_Dudes.mscz||g' -e 's|Triumph.mscz||g' demos/CMakeLists.txt

# Force Fedora specific flags:
find . -name CMakeLists.txt -exec sed -i -e 's|-m32|%{optflags}|' -e 's|-O3|%{optflags}|' {} \;

# Do not build the bundled qt scripting interface:
sed -i 's|BUILD_SCRIPTGEN TRUE|BUILD_SCRIPTGEN FALSE|' %{name}/CMakeLists.txt

# Fix EOL encoding
sed 's|\r||' thirdparty/rtf2html/README > tmpfile
touch -r thirdparty/rtf2html/README tmpfile
mv -f tmpfile thirdparty/rtf2html/README

# Disable rpath
sed -i '/rpath/d' CMakeLists.txt

####################################################################################################

%build
# Build the actual program
mkdir -p build
pushd build
   %cmake -DCMAKE_BUILD_TYPE=RELEASE         \
          -DCMAKE_CXX_FLAGS="%{optflags} -fsigned-char"    \
          -DCMAKE_CXX_FLAGS_RELEASE="%{optflags} -std=c++11 -fPIC -O2 -DDEBUG -fsigned-char" \
          -DBUILD_LAME=ON \
          -DUSE_SYSTEM_QTSINGLEAPPLICATION=1 \
          -DUSE_SYSTEM_FREETYPE=1 \
          -DQT_QMAKE_EXECUTABLE=/usr/bin/qmake-qt5 \
          ..
   make PREFIX=/usr lrelease %{?_smp_mflags}
%if 0%{?fedora} <= 26
   cp ../all.h . # cmake dependency issue in fc26 use source PCH
%endif
   make PREFIX=/usr manpages %{?_smp_mflags}
   make PREFIX=/usr %{?_smp_mflags} VERBOSE=1
   pushd rdoc
      make PREFIX=/usr
   popd
popd

####################################################################################################

%install
pushd build
make install PREFIX=/usr DESTDIR=%{buildroot}
popd
pushd build/rdoc
make install PREFIX=/usr DESTDIR=%{buildroot}
popd

mkdir -p %{buildroot}/%{_datadir}/applications
cp -a build/mscore.desktop %{buildroot}/%{_datadir}/applications

# Install fonts
mkdir -p %{buildroot}/%{_fontdir}
mkdir -p %{buildroot}/%{_fontdir}/bravura
mkdir -p %{buildroot}/%{_fontdir}/gootville
install -pm 644 fonts/*.ttf %{buildroot}/%{_fontdir}
install -pm 644 fonts/bravura/*.otf %{buildroot}/%{_fontdir}
install -pm 644 fonts/bravura/*.json %{buildroot}/%{_fontdir}/bravura
install -pm 644 fonts/gootville/*.otf %{buildroot}/%{_fontdir}
install -pm 644 fonts/gootville/*.json %{buildroot}/%{_fontdir}/gootville/
install -pm 644 fonts/mscore/*.ttf %{buildroot}/%{_fontdir}
install -pm 644 fonts/mscore/*.json %{buildroot}/%{_fontdir}
install -pm 644 fonts/*.xml %{buildroot}/%{_fontdir}

# mscz
install -pm 0644 share/templates/*.mscz %{buildroot}/%{_datadir}/%{name}-%{short_version}/demos/
# symlinks to be safe
pushd %{buildroot}/%{_datadir}/%{name}-%{short_version}/demos/
for i in *.mscz; do
  ln -s %{_datadir}/%{name}-%{short_version}/demos/$i ../templates/$i
done
popd

pushd %{buildroot}/%{_fontdir}
cd bravura
ln -s ../Bravura.otf .
ln -s ../BravuraText.otf .
cd ../gootville
ln -s ../Gootville.otf .
ln -s ../GootvilleText.otf .
cd ..
popd

# Mime type
mkdir -p %{buildroot}/%{_datadir}/mime/packages
install -pm 644 %{SOURCE1} %{buildroot}/%{_datadir}/mime/packages/

# Desktop file
desktop-file-install \
   --dir=%{buildroot}/%{_datadir}/applications \
   --add-category="X-Notation" \
   --remove-category="Sequencer" \
   --remove-category="AudioVideoEditing" \
   --add-mime-type="audio/midi" \
   --add-mime-type="text/x-lilypond" \
   --add-mime-type="application/xml" \
   %{buildroot}/%{_datadir}/applications/%{name}.desktop

# Move images to the freedesktop location
mkdir -p %{buildroot}/%{_datadir}/icons/hicolor/{32x32,64x64}/apps/
mkdir -p %{buildroot}/%{_datadir}/icons/hicolor/{32x32,64x64}/mimetypes/
cp -a mscore/data/mscore.xpm \
   %{buildroot}/%{_datadir}/icons/hicolor/32x32/mimetypes/application-x-musescore.xpm
cp -a mscore/data/mscore.xpm \
   %{buildroot}/%{_datadir}/icons/hicolor/32x32/apps/
cp -a mscore/data/mscore.png \
   %{buildroot}/%{_datadir}/icons/hicolor/64x64/mimetypes/application-x-musescore.png
cp -a mscore/data/mscore.png \
   %{buildroot}/%{_datadir}/icons/hicolor/64x64/apps/

# Manpage
mkdir -p %{buildroot}/%{_mandir}/man1
install -pm 644 build/%{name}.1 %{buildroot}/%{_mandir}/man1/

# There are many doc files spread around the tarball. Let's collect them
mv thirdparty/rtf2html/ChangeLog        ChangeLog.rtf2html
mv thirdparty/rtf2html/COPYING.LESSER   COPYING.LESSER.rtf2html
mv thirdparty/rtf2html/README           README.rtf2html
mv thirdparty/rtf2html/README.mscore    README.mscore.rtf2html
mv thirdparty/rtf2html/README.ru        README.ru.rtf2html
mv share/wallpaper/COPYRIGHT            COPYING.wallpaper
mv %{buildroot}%{_datadir}/soundfonts/MuseScore_General-License.md COPYING.MuseScore_General
mv fonts/bravura/OFL.txt                COPYING.OFL

# Add AppStream metadata
install -Dm 0644 -p %{SOURCE2} \
        %{buildroot}%{_datadir}/appdata/%{font_family_name}.metainfo.xml

####################################################################################################

%check
# iotest seems outdated. Skipping.
# rendertest needs the X server. Skipping.

####################################################################################################

%files
%doc README*
%license LICENSE.GPL COPYING*
%{_bindir}/mscore
%{_bindir}/musescore
%{_datadir}/%{name}-%{short_version}/
%exclude %{_datadir}/%{name}-%{short_version}/manual/
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/applications/%{name}.desktop
%exclude %{_datadir}/mime/packages/musescore.xml
%{_datadir}/mime/packages/mscore.xml
%{_mandir}/man1/*
%{_datadir}/soundfonts/MuseScore_General.sf3

####################################################################################################

%files doc
%doc %{_datadir}/%{name}-%{short_version}/manual/

####################################################################################################

%_font_pkg %{font_family_name}*.ttf
%{_datadir}/appdata/%{font_family_name}.metainfo.xml
%{_datadir}/fonts/mscore/*.json
%{_datadir}/fonts/mscore/*.otf
%{_datadir}/fonts/mscore/*.ttf
%{_datadir}/fonts/mscore/*.xml
%{_datadir}/fonts/mscore/MScoreText.ttf
%{_datadir}/fonts/mscore/bravura/
%{_datadir}/fonts/mscore/gootville/

####################################################################################################

%changelog
* Thu Mar 14 2019 Fabrice Salvaire <fabrice.salvaire@orange.fr> - 3.0.5-1
- MuseScore 3

* Fri Sep 21 2018 Jan Grulich <jgrulich@redhat.com> - 2.2.1-6
- rebuild (qt5)

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jun 21 2018 Rex Dieter <rdieter@fedoraproject.org> - 2.2.1-4
- rebuild (qt5)

* Thu May 31 2018 Orcan Ogetbil <oget[DOT]fedora[AT]gmail[DOT]com> - 2.2.1-3
- Fix missing include for qt >= 5.11 (RHBZ#1584834)

* Sun May 27 2018 Rex Dieter <rdieter@fedoraproject.org> - 2.2.1-2
- rebuild (qt5)

* Wed Apr 04 2018 Orcan Ogetbil <oget[DOT]fedora[AT]gmail[DOT]com> - 2.2.1-1
- Update to 2.2.1

* Wed Feb 14 2018 Jan Grulich <jgrulich@redhat.com> - 2.1.0-12
- rebuild (qt5)

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.1.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Jan 05 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 2.1.0-10
- Remove (hopefully) last dependency on qt4

* Fri Jan 05 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 2.1.0-9
- Remove obsolete scriptlets

* Mon Jan 01 2018 Rex Dieter <rdieter@fedoraproject.org> - 2.1.0-8
- rebuild (qt5)

* Mon Dec 25 2017 Brendan Jones <brendan.jones.it@gmail.com> - 2.1.0-7
- Link against full template path

* Mon Dec 25 2017 Brendan Jones <brendan.jones.it@gmail.com> - 2.1.0-6
- Correct mscz link

* Mon Nov 27 2017 Rex Dieter <rdieter@fedoraproject.org> - 2.1.0-5
- rebuild (qt5)

* Mon Nov 20 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 2.1.0-4
- Use proper qtsingleapplication (qt5)

* Sun Oct 29 2017 Brendan Jones <brendan.jones.it@gmail.com> - 2.1.0-3
- Use system libs

* Sat Oct 21 2017 Brendan Jones <brendan.jones.it@gmail.com> - 2.1.0-2
- Remove non-free scores
- Fix pch project depends
- Reorder patches

* Tue Oct 17 2017 Brendan Jones <brendan.jones.it@gmail.com> - 2.1.0-1
- Update to 2.1

* Wed Oct 11 2017 Rex Dieter <rdieter@fedoraproject.org> - 2.0.3-10
- BR: qt5-qtbase-private-devel

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.3-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.3-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sun Jun 18 2017 Orcan Ogetbil <oget[DOT]fedora[AT]gmail[DOT]com> - 2.0.3-7
- Removed BR: qt5-qtquick1-devel as it is no longer in Fedora

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sat Nov 19 2016 Peter Robinson <pbrobinson@fedoraproject.org> 2.0.3-4
- Rebuild (Power64)

* Mon May 09 2016 Brendan Jones <brendan.jones.it@gmail.com> 2.0.3-3
- Font locations

* Fri May 06 2016 Brendan Jones <brendan.jones.it@gmail.com> 2.0.3-2
- correct load and font errors

* Sun Apr 24 2016 Brendan Jones <brendan.jones.it@gmail.com> 2.0.3-1
- Update to 2.0.3
- fix make job flags
- rename modified patches

* Sat Feb 27 2016 Brendan Jones <brendan.jones.it@gmail.com> 2.0.2-1
- Update to 2.0.2

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Nov 19 2015 Brendan Jones <brendan.jones.it@gmail.com> 2.0.1-6
- Fix fonts_tabulature.xml location bug rhbz#1236965 rhbz#1262528

* Wed Sep 16 2015 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 2.0.1-5
- added backport fixing compilation with Qt5.5 - rhbz#1263806

* Tue Jul 14 2015 Brendan Jones <brendan.jones.it@gmail.com> 2.0.1-4
- Rebuilt

* Tue Jun 30 2015 Brendan Jones <brendan.jones.it@gmail.com> 2.0.1-3
- Fix font locations

* Tue Jun 23 2015 Brendan Jones <bsjones@fedoraproject.org> - 2.0.1-2
- Clean up change log

* Tue Jun 23 2015 Brendan Jones <bsjones@fedoraproject.org> - 2.0.1-1
- Update to 2.0.1 - patches provided by Bodhi Zazen

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Apr 29 2015 Tom Callaway <spot@fedoraproject.org> - 2.0.0-3
- do not strip bits when installing (bz 1215956)

* Sat Apr 25 2015 Tom Callaway <spot@fedoraproject.org> - 2.0.0-2
- add BR: doxygen
- add -fsigned-char for ARM

* Sat Apr 25 2015 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 2.0.0-1
- Remove mp3 support to fix FTBFS
- Add pulseaudio-libs-devel to BR

* Tue Nov 18 2014 Parag Nemade <pnemade AT redhat DOT com> - 1.3-8
- Add metainfo file to show mscore-MuseJazz font in gnome-software

* Thu Oct 02 2014 Rex Dieter <rdieter@fedoraproject.org> 1.3-7
- update mime scriptlet

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Feb 26 2014 Dan Horák <dan[at]danny.cz> - 1.3-4
- fix FTBFS (#992300)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Apr 12 2013 Tom Callaway <spot@fedoraproject.org> - 1.3-2
- perl(Pod::Usage) needed for font generation

* Fri Apr 12 2013 Tom Callaway <spot@fedoraproject.org> - 1.3-1
- update to 1.3
- remove mscore/demos/prelude.mscx from source tarball (it is non-free, see bz951379)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Mar 13 2012 Orcan Ogetbil <oget[DOT]fedora[AT]gmail[DOT]com> - 1.2-1
- Update to 1.2.

* Sat Mar 03 2012 Orcan Ogetbil <oget[DOT]fedora[AT]gmail[DOT]com> - 1.1-4
- Fix accidontals crash RHBZ#738044

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-3
- Rebuilt for c++ ABI breakage

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Jul 28 2011 Orcan Ogetbil <oget[DOT]fedora[AT]gmail[DOT]com> - 1.1-1
- Update to 1.1.

* Tue Feb 08 2011 Orcan Ogetbil <oget[DOT]fedora[AT]gmail[DOT]com> - 1.0-1
- Update to 1.0.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.6.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Sep 26 2010 Orcan Ogetbil <oget[DOT]fedora[AT]gmail[DOT]com> - 0.9.6.3-1
- Update to 0.9.6.3

* Thu Aug 19 2010 Orcan Ogetbil <oget[DOT]fedora[AT]gmail[DOT]com> - 0.9.6.2-1
- Update to 0.9.6.2

* Tue Jul 20 2010 Orcan Ogetbil <oget[DOT]fedora[AT]gmail[DOT]com> - 0.9.6.1-1
- Update to 0.9.6.1

* Mon Jun 14 2010 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> 0.9.6-1
- Update to 0.9.6
- Split documentation into its own package
- Move some gcc warning fixes into a patch

* Tue Dec 22 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> 0.9.5-3
- Fix build flags on F-11

* Tue Dec 22 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> 0.9.5-2
- Add default soundfont support for exported audio files
- Rebuild against new libsndfile for additional functionality
- Drop F-10 related bits from specfile
- Make fonts subpackage noarch
- Fix build failure on arm architecture

* Fri Aug 21 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> 0.9.5-1
- Update to 0.9.5

* Wed Aug 05 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> 0.9.4-6
- Update the .desktop file

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jun 11 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> 0.9.4-4
- Font package cleanup for F-12 (RHBZ#493463)
- One specfile for all releases

* Mon Mar 23 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> 0.9.4-3.fc10.1
- Add BR: tetex-font-cm-lgc for Fedora < 11

* Mon Mar 23 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> 0.9.4-3
- Add Provides: musescore = %%{name}-%%{version}
- Replace "fluid-soundfont" requirement with "soundfont2-default"

* Fri Mar 06 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> 0.9.4-2
- Add extra BR:tex-cm-lgc for F-11+. This is necessary to build the fonts from source
- Update icon scriptlets according to the new guidelines

* Sat Feb 21 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> 0.9.4-1
- Initial Fedora build
