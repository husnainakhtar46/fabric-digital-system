from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class FabricSpec:
    # Identity
    fabric_code: str
    
    # Origin
    supplier: Optional[str] = ""
    
    # General
    moq: Optional[str] = ""
    category: Optional[str] = ""
    status: Optional[str] = ""
    
    # Specs
    composition: Optional[str] = ""
    shade: Optional[str] = ""
    
    # Technical
    weight: Optional[str] = ""
    finish: Optional[str] = ""
    width: Optional[str] = ""
    
    # Shrinkage
    warp_shrink: Optional[str] = ""
    weft_shrink: Optional[str] = ""
    
    # Weave/Stretch
    weave: Optional[str] = ""
    stretch: Optional[str] = ""
    growth: Optional[str] = ""
    
    # Media Links
    main_img_id: Optional[str] = ""
    wash_ids: List[str] = field(default_factory=list)

    def to_sheet_row(self) -> List[str]:
        """Converts the object to a list of strings for Google Sheets row."""
        # Join wash IDs with comma if multiple
        wash_ids_str = ",".join(self.wash_ids) if self.wash_ids else ""
        
        return [
            self.fabric_code,
            self.supplier,
            self.moq, self.category, self.status,
            self.composition, self.shade,
            self.weight, self.finish, self.width,
            self.warp_shrink, self.weft_shrink,
            self.weave, self.stretch, self.growth,
            self.main_img_id, wash_ids_str
        ]
