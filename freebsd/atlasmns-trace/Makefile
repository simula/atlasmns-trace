# Created by: Thomas Dreibholz <dreibh@iem.uni-due.de>
# $FreeBSD$

PORTNAME=	atlasmns-trace
PORTVERSION=	0.3.3~alpha1.1
CATEGORIES=	benchmarks
MASTER_SITES=	https://packages.nntb.no/software/atlasmns-trace-service

MAINTAINER=	dreibh@iem.uni-due.de
COMMENT=	AtlasMNS Trace

LICENSE=	GPLv3+
LICENSE_FILE=	${WRKSRC}/COPYING

LIB_DEPENDS=    libpqxx4.so:databases/postgresql-libpqxx4 \
                libhipercontracer.so:benchmarks/hipercontracer
RUN_DEPENDS=    trace-importer:benchmarks/hipercontracer

USES=		tar:xz cmake

CMAKE_ARGS+=    -DCMAKE_INSTALL_MANDIR=${PREFIX}/man

.include <bsd.port.mk>
