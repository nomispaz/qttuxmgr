#!/bin/bash

#get linux distro
curDistro=$(lsb_release -a | grep "Distributor ID" | tr "[:upper:]" "[:lower:]" | cut -f 2)
screenfetch

while true
do
    echo "1) Sync repository"
    echo "2) Perform Update"
    echo "3) Clean packages and kernel"
    echo "4) List Kernels"
    echo "5) Exit"
    echo "Perform action (<Number>): "
    read action
    case "$action" in
        1)  case "$curDistro" in
                gentoo) sudo emerge --sync
                        ;;
            esac
            ;;
        2)  case "$curDistro" in
                gentoo) sudo mount -o remount,size=8G /var/tmp/portage
                        sudo emerge -avuDNg @world
                        sudo mount -o remount,size=1M /var/tmp/portage
                        ;;
            esac
            ;;
        3)  case "$curDistro" in
                gentoo) sudo emerge --ask --depclean
                        sudo eclean packages
                        sudo eclean distfiles
                        sudo eclean-kernel -n 2
                        ;;
            esac
            ;;
        4)  case "$curDistro" in
                gentoo) sudo eselect kernel list
                        ;;
            esac
            ;;
        5)  break
            ;;
    esac
done
