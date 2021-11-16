import json
import os
from datetime import datetime

#region Data-Classes
class DataSource():
    # parent class for all datatypes
    def __init__(self, layerId=None, nameFull=None, nameShort=None, urlInfo=None, versionDate=None, extent=None, dateCreated=None, dateModified=None, epsg=None) -> None:
        self.layerId = layerId
        self.nameFull = nameFull
        self.nameShort = nameShort
        self.urlInfo = urlInfo
        self.versionDate = versionDate
        self.extent = extent
        self.epsg = epsg
        if dateCreated != None:
            self.dateCreated = datetime.fromisoformat(dateCreated)
        else: 
            self.dateCreated = datetime.utcnow()

        if dateModified != None:
            self.dateModified = datetime.fromisoformat(dateCreated)
        else: 
            self.dateModified = datetime.utcnow()

    def ToDict(self):
        return {
            'layerId' : self.layerId,
            'nameFull': self.nameFull,
            'nameShort': self.nameShort,
            'urlInfo':self.urlInfo,
            'versionDate':self.versionDate,
            'extent':self.extent,
            'epsg':self.epsg,
            'dateCreated':self.dateCreated.isoformat(),
            'dateModified':self.dateModified.isoformat()
        }

    def __repr__(self) -> str:
        return f"{self.layerId}, {self.nameShort}, {self.versionDate}"

class DataTiles(DataSource):
    # handles a Datasource with individual tiles.

    class Tile():
        # contains Data for individual tile
        pass

    pass

class DataPackage(DataSource):
    # contains vars and methods to handle Data in form of a Package (ZIP, RAR, etc.) 
    def __init__(self, layerId=None, nameFull=None, nameShort=None, urlInfo=None, urlDownload=None) -> None:
        super().__init__(layerId=layerId, nameFull=nameFull, nameShort=nameShort, urlInfo=urlInfo)
        self.urlDownload = urlDownload # Url for single file download
    pass

class DataLayers(DataSource):
    # handles a Datasource in form of individual layers
    pass

#endregion

class Atlas():

    rootPath = './atlas'
    meta = {
        'DatetimeCreated' : None,
        'DatetimeModified' : None,
        'Version' : None,
        'NumSources' : None,
    }
    dataSources = {}

    def __init__(self) -> None:
        if not (os.path.isdir('./atlas')):
            self.CreateNewAtlas()
        self.LoadAtlas()

    def CreateNewAtlas(self, targetPath='.'):
        Atlas.rootPath = os.path.join(targetPath, 'atlas')
        if os.path.isdir(Atlas.rootPath):
            raise Exception("Atlas already exists. Can't create new Atlas on this location")
        else:
            os.makedirs(Atlas.rootPath)
            Atlas.meta['DatetimeCreated'] = datetime.utcnow().isoformat()
            Atlas.meta['DatetimeModified'] = datetime.utcnow().isoformat()
            Atlas.meta['Version'] = 0
            self.UpdateAtlasMetadata()
    
    def LoadAtlas(self):
        self.LoadAtlasMetadata()
        self.LoadDatasourcesIntoAtlas()
        self.UpdateAtlasMetadata()

    def WriteAtlas(self, updateExisting=True, forceOverwrite=False):
        for id, ds in Atlas.dataSources.items():
            print(f"Writing {id}")
            self.WriteDatasource(ds, forceOverwrite=forceOverwrite, updateExisting=updateExisting)

    def LoadDatasourcesIntoAtlas(self):
        # read datasources from json file in atlas directory
        for fname in os.listdir(Atlas.rootPath):
            print (fname)
            id = fname.replace('.json', '')
            if fname[0] != '_':
                Atlas.dataSources[id] = self.LoadDatasource( os.path.join(Atlas.rootPath,  fname))

    def LoadDatasource(self, fname):
        # load single Datasource and reutrn object
        with open(os.path.join(fname), 'r') as f:
            jdata = json.load(f)
            return DataSource(**jdata)
    
    def WriteDatasource(self, ds:DataSource, forceOverwrite=False, updateExisting=True):
        # write json file from Datasource object
        fname = os.path.join(Atlas.rootPath, ds.layerId+'.json')
        isNewVersion = False
        if (os.path.isfile(fname)):
            # datasource already exists
            dsExisting = self.LoadDatasource(fname=fname)
            if ds.dateModified > dsExisting.dateModified:
                # current object is newer, existing will be replaced
                ds.dateCreated = dsExisting.dateCreated
                isNewVersion = True
        else:
            # new datasource
            isNewVersion = True
        
        if (forceOverwrite or (isNewVersion and updateExisting )):
            with open(fname, 'w') as f:
                json.dump( ds.ToDict(), f , indent='\t')

    def UpdateDatasource(self, *ds:DataSource):
        for i in ds:
            Atlas.dataSources[i.layerId] = i

    def UpdateAtlasMetadata(self):
        Atlas.meta['DatetimeModified'] = datetime.utcnow().isoformat()
        Atlas.meta['Version'] += 1
        Atlas.meta['NumSources'] = len(self.dataSources)
        with open(os.path.join( Atlas.rootPath, '_meta.json' ), 'w') as f:
            json.dump( Atlas.meta, f, indent="\t")
    
    def LoadAtlasMetadata(self):
        with open(os.path.join(Atlas.rootPath, '_meta.json'), 'r') as f:
            Atlas.meta = json.load(f)

    # ID-Path: <Domain>.<issuer>.<name>
    # example: ch.swisstopo.swissimage10
    
    pass


if __name__ == '__main__':

    # Init Atlas
    a = Atlas()

    # Create Datasource
    # ds1 = DataSource(layerId="ch.swisstopo.swissimage-product_1946", 
    #                 nameFull="SWISSIMAGE HIST 1946: Das Orthophotomosaik der Schweiz von 1946",
    #                 nameShort="SWISSIMAGE HIST 1946",
    #                 urlInfo="https://www.swisstopo.admin.ch/de/geodata/images/ortho/swissimage-hist-1946.html")

    # ds2 = DataSource(layerId="ch.swisstopo.swissimage-product", 
    #                 nameFull="SWISSIMAGE: Das digitale Orthophotomosaik der Schweiz",
    #                 nameShort="SWISSIMAGE10",
    #                 urlInfo="https://www.swisstopo.admin.ch/de/geodata/images/ortho/swissimage10.html")

    # a.UpdateDatasource(ds1, ds2)
    a.WriteAtlas()

    print (a.dataSources)

    pass