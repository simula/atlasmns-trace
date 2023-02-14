# Created by: Thomas Dreibholz <thomas.dreibholz@gmail.com>
# $FreeBSD$

PORTNAME=	atlasmns-trace
PORTVERSION=	0.4.9
CATEGORIES=	benchmarks
MASTER_SITES=	https://packages.nntb.no/software/atlasmns-trace-service

MAINTAINER=	thomas.dreibholz@gmail.com
COMMENT=	AtlasMNS Trace

LICENSE=	GPLv3+
LICENSE_FILE=	${WRKSRC}/COPYING

LIB_DEPENDS=    libpqxx4.so:databases/postgresql-libpqxx4 \
                libhipercontracer.so:benchmarks/hipercontracer
RUN_DEPENDS=    trace-importer:benchmarks/hipercontracer

USES=		tar:xz cmake

CMAKE_ARGS+=    -DCMAKE_INSTALL_MANDIR=${PREFIX}/man

.include <bsd.port.mk>
